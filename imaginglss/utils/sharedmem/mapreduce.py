import backends
import threading
import heapq
import gc
import os
import Queue as queue
__all__ = ['MapReduce', 'MapReduceByThread']

def MapReduceByThread(np=None):
    return MapReduce(backend=backends.ThreadBackend, np=np)

class MapReduce(object):
    def __init__(self, backend=backends.ProcessBackend, np=None):
        """ if np is 0, run in serial """
        self.backend = backend
        if np is None:
            self.np = backends.cpu_count()
        else:
            self.np = np

    def main(self, pg, Q, R, sequence, realfunc):
        # get and put will raise SlaveException
        # and terminate the process.
        # the exception is muted in ProcessGroup,
        # as it will only be dispatched from master.
        while True:
            capsule = pg.get(Q)
            if capsule is None:
                return
            if len(capsule) == 1:
                i, = capsule
                work = sequence[i]
            else:
                i, work = capsule
            self.ordered.move(i)
            r = realfunc(work)
            pg.put(R, (i, r))


    def __enter__(self):
        self.critical = self.backend.LockFactory()
        self.ordered = backends.Ordered(self.backend)
        return self

    def __exit__(self, *args):
        self.ordered = None
        pass

    def map(self, func, sequence, reduce=None, star=False):
        def realreduce(r):
            if reduce:
                if isinstance(r, tuple):
                    return reduce(*r)
                else:
                    return reduce(r)
            return r

        def realfunc(i):
            if star: return func(*i)
            else: return func(i)

        if self.np == 0 or backends.get_debug():
            #Do this in serial
            return [realreduce(realfunc(i)) for i in sequence]

        Q = self.backend.QueueFactory(64)
        R = self.backend.QueueFactory(64)
        self.ordered.reset()

        pg = backends.ProcessGroup(main=self.main, np=self.np,
                backend=self.backend,
                args=(Q, R, sequence, realfunc))

        pg.start()

        L = []
        N = []
        def feeder(pg, Q, N):
            #   will fail silently if any error occurs.
            j = 0
            try:
                for i, work in enumerate(sequence):
                    if not hasattr(sequence, '__getitem__'):
                        pg.put(Q, (i, work))
                    else:
                        pg.put(Q, (i, ))
                    j = j + 1
                N.append(j)

                for i in range(self.np):
                    pg.put(Q, None)
            except backends.StopProcessGroup:
                return
            finally:
                pass
        feeder = threading.Thread(None, feeder, args=(pg, Q, N))
        feeder.start() 

        # we run fetcher on main thread to catch exceptions
        # raised by reduce 
        count = 0
        try:
            while True:
                try:
                    capsule = pg.get(R)
                except queue.Empty:
                    continue
                except backends.StopProcessGroup:
                    raise pg.get_exception()
                capsule = capsule[0], realreduce(capsule[1])
                heapq.heappush(L, capsule)
                count = count + 1
                if len(N) > 0 and count == N[0]: 
                    # if finished feeding see if all
                    # results have been obtained
                    break
            rt = []
#            R.close()
#            R.join_thread()
            while len(L) > 0:
                rt.append(heapq.heappop(L)[1])
            pg.join()
            feeder.join()
            assert N[0] == len(rt)
            return rt
        except BaseException as e:
            pg.killall()
            pg.join()
            feeder.join()
            raise 

def main2():
    import time
    import os
    import signal
    import numpy
    m = MapReduce(np=8)
    def work(i):
    #    with m.ordered:
    #        time.sleep(1)
        print i
        return i
    print m.map(work, range(18))
