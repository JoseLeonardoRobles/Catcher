import datetime as DT
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import scipy.spatial as spatial

def fmt(x, y, is_date):
    if is_date:
        x = mdates.num2date(x).strftime("%Y-%m-%d")
        return 'x: {x}\ny: {y}'.format(x=x, y=y)
    else:
        return 'x: {x:0.2f}\ny: {y:0.2f}'.format(x=x, y=y)


class FollowDotCursor(object):
    """Display the x,y location of the nearest data point."""
    def __init__(self, ax, x, y, tolerance=5, formatter=fmt, offsets=(-20, 20)):
        try:
            x = np.asarray(x, dtype='float')
            self.is_date = False
        except (TypeError, ValueError):
            x = np.asarray(mdates.date2num(x), dtype='float')
            self.is_date = True
        y = np.asarray(y, dtype='float')
        self._points = np.column_stack((x, y))
        self.offsets = offsets
        self.scale = x.ptp()
        self.scale = y.ptp() / self.scale if self.scale else 1
        self.tree = spatial.cKDTree(self.scaled(self._points))
        self.formatter = formatter
        self.tolerance = tolerance
        self.ax = ax
        self.fig = ax.figure
        self.ax.xaxis.set_label_position('top')
        self.dot = ax.scatter(
            [x.min()], [y.min()], s=130, color='green', alpha=0.7)
        self.annotation = self.setup_annotation()
        plt.connect('motion_notify_event', self)

    def scaled(self, points):
        points = np.asarray(points)
        return points * (self.scale, 1)

    def __call__(self, event):
        ax = self.ax
        # event.inaxes is always the current axis. If you use twinx, ax could be
        # a different axis.
        if event.inaxes == ax:
            x, y = event.xdata, event.ydata
        elif event.inaxes is None:
            return
        else:
            inv = ax.transData.inverted()
            x, y = inv.transform([(event.x, event.y)]).ravel()
        annotation = self.annotation
        x, y = self.snap(x, y)
        annotation.xy = x, y
        annotation.set_text(self.formatter(x, y, self.is_date))
        self.dot.set_offsets((x, y))
        bbox = ax.viewLim
        event.canvas.draw()

    def setup_annotation(self):
        """Draw and hide the annotation box."""
        annotation = self.ax.annotate(
            '', xy=(0, 0), ha = 'right',
            xytext = self.offsets, textcoords = 'offset points', va = 'bottom',
            bbox = dict(
                boxstyle='round,pad=0.5', fc='yellow', alpha=0.75),
            arrowprops = dict(
                arrowstyle='->', connectionstyle='arc3,rad=0'))
        return annotation

    def snap(self, x, y):
        """Return the value in self.tree closest to x, y."""
        dist, idx = self.tree.query(self.scaled((x, y)), k=1, p=1)
        try:
            return self._points[idx]
        except IndexError:
            # IndexError: index out of bounds
            return self._points[0]

x = [DT.date.today()+DT.timedelta(days=i) for i in [10,20,30,40,50]]
y = [6,7,8,9,10]

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.scatter(x, y)
cursor = FollowDotCursor(ax, x, y)
fig.autofmt_xdate()
plt.show()
        
