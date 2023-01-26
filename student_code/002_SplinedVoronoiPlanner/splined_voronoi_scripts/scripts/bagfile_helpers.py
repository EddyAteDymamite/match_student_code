import rosbag


def get_contents_from_bagfile(filename: str):
    bag = rosbag.Bag(filename)
    bag_contents = {}
    for topic, msg, t in bag.read_messages(topics=[]):
        # assuming there is only one message per topic!
        bag_contents[topic] = msg
    bag.close()
    return bag_contents


class PlanningBagContents:
    def __init__(
        self, filename: str = "plan_00000.bag", skip_maps: bool = False
    ) -> None:
        self.skip_maps = skip_maps
        self.bag_contents = {}
        self.read_rosbag(filename)

        self.start_pose = self.bag_contents["start_pose"]
        self.goal_pose = self.bag_contents["goal_pose"]
        self.formation_max_curvature: float = self.bag_contents[
            "formation_max_curvature"
        ].data
        self.path = self.bag_contents["path"]
        if not self.skip_maps:
            self.map_data = self.bag_contents["map_data"]

    def read_rosbag(self, filename: str):
        bag = rosbag.Bag(filename)
        for topic, msg, t in bag.read_messages(
            topics=[], connection_filter=self.filter_map_topics
        ):
            # assuming there is only one message per topic!
            self.bag_contents[topic] = msg
        bag.close()

    def filter_map_topics(self, topic, datatype, md5sum, msg_def, header):
        # print(datatype)
        if self.skip_maps and datatype == "nav_msgs/OccupancyGrid":
            # print("skipping topic with occupancy grid")
            return False
        return True


class MakeNavPlanWithStatsBagContents(PlanningBagContents):
    def __init__(
        self, filename: str = "plan_00000.bag", skip_maps: bool = False
    ) -> None:
        super().__init__(filename, skip_maps)
        self.planning_status_code: int = self.bag_contents["planning_status_code"].data
        self.total_time: float = self.bag_contents["total_time_taken_for_planning"].data
        self.path_on_voronoi = self.bag_contents["path_on_voronoi"]
        self.sparse_path = self.bag_contents["sparse_path"]
        self.optimized_sparse_path = self.bag_contents["optimized_sparse_path"]
        self.spline_tangent_lengths = self.bag_contents["spline_tangent_lengths"].data
        if not self.skip_maps:
            self.voronoi_data = self.bag_contents["voronoi_data"]
