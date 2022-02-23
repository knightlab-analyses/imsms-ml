class FeatureFilter:
    pass


class ZebraFilter(FeatureFilter):
    def __init__(self, cov_thresh, cov_file):
        self.filter_type = "zebra"
        self.cov_thresh = cov_thresh
        self.cov_file = cov_file

    def __str__(self):
        return "Zebra:" + str(self.cov_thresh)
