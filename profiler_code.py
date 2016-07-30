import cProfile
import pstats
import StringIO

pr = cProfile.Profile()
pr.enable()


pr.disable()
s = StringIO.StringIO()
sortby = 'time'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()

logger.log(s.getvalue())

print s.getvalue()
