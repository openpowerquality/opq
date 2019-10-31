import typing

import reports


class Gaps:
    def __init__(self, boxes: typing.List[str]):
        self.boxes = boxes
        self.gaps = []

        box_range = list(range(len(self.boxes)))
        for _ in box_range:
            self.gaps.append([0 for _ in box_range])

    def add_gap(self, from_box: int, to_box: int, gap: int) -> 'Gaps':
        from_box_idx = self.boxes.index(str(from_box))
        to_box_idx = self.boxes.index(str(to_box))
        self.gaps[from_box_idx][to_box_idx] = gap
        self.gaps[to_box_idx][from_box_idx] = gap
        return self

    def __str__(self):
        s = "     %s\n" % " ".join(self.boxes)
        for i, box in enumerate(self.boxes):
            gaps_str = " ".join(map(lambda v: str(v).ljust(4), self.gaps[i]))
            s += "%s %s\n" % (box, gaps_str)

        return s


if __name__ == "__main__":
    gaps_east_west = Gaps(reports.boxes)
    gaps_east_west \
        .add_gap(1000, 1001, 10) \
        .add_gap(1000, 1002, 0) \
        .add_gap(1000, 1003, 9) \
        .add_gap(1000, 1005, 13) \
        .add_gap(1000, 1006, 8) \
        .add_gap(1000, 1007, 9) \
        .add_gap(1000, 1008, 8) \
        .add_gap(1000, 1009, 5) \
        .add_gap(1000, 1010, 2) \
        .add_gap(1000, 1021, 1) \
        .add_gap(1000, 1022, 6) \
        .add_gap(1000, 1023, 8) \
        .add_gap(1000, 1024, 10) \
        .add_gap(1000, 1025, 4) \
        .add_gap(1001, 1002, 10) \
        .add_gap(1001, 1003, 12) \
        .add_gap(1001, 1005, 11) \
        .add_gap(1001, 1006, 9) \
        .add_gap(1001, 1007, 10) \
        .add_gap(1001, 1008, 11) \
        .add_gap(1001, 1009, 16) \
        .add_gap(1001, 1010, 7) \
        .add_gap(1001, 1021, 11) \
        .add_gap(1001, 1022, 10) \
        .add_gap(1001, 1023, 9) \
        .add_gap(1001, 1024, 8) \
        .add_gap(1001, 1025, 15) \
        .add_gap(1002, 1003, 9) \
        .add_gap(1002, 1005, 13) \
        .add_gap(1002, 1006, 8) \
        .add_gap(1002, 1007, 9) \
        .add_gap(1002, 1008, 8) \
        .add_gap(1002, 1009, 5) \
        .add_gap(1002, 1010, 2) \
        .add_gap(1002, 1021, 1) \
        .add_gap(1002, 1022, 6) \
        .add_gap(1002, 1023, 8) \
        .add_gap(1002, 1024, 10) \
        .add_gap(1002, 1025, 4) \
        .add_gap(1003, 1005, 11) \
        .add_gap(1003, 1006, 10) \
        .add_gap(1003, 1007, 11) \
        .add_gap(1003, 1008, 10) \
        .add_gap(1003, 1009, 15) \
        .add_gap(1003, 1010, 7) \
        .add_gap(1003, 1021, 11) \
        .add_gap(1003, 1022, 9) \
        .add_gap(1003, 1023, 10) \
        .add_gap(1003, 1024, 9) \
        .add_gap(1003, 1025, 13) \
        .add_gap(1005, 1006, 7) \
        .add_gap(1005, 1007, 8) \
        .add_gap(1005, 1008, 10) \
        .add_gap(1005, 1009, 14) \
        .add_gap(1005, 1010, 7) \
        .add_gap(1005, 1021, 11) \
        .add_gap(1005, 1022, 9) \
        .add_gap(1005, 1023, 5) \
        .add_gap(1005, 1024, 7) \
        .add_gap(1005, 1025, 14) \
        .add_gap(1006, 1007, 1) \
        .add_gap(1006, 1008, 9) \
        .add_gap(1006, 1009, 14) \
        .add_gap(1006, 1010, 6) \
        .add_gap(1006, 1021, 10) \
        .add_gap(1006, 1022, 8) \
        .add_gap(1006, 1023, 7) \
        .add_gap(1006, 1024, 6) \
        .add_gap(1006, 1025, 9) \
        .add_gap(1007, 1008, 10) \
        .add_gap(1007, 1009, 15) \
        .add_gap(1007, 1010, 7) \
        .add_gap(1007, 1021, 11) \
        .add_gap(1007, 1022, 9) \
        .add_gap(1007, 1023, 8) \
        .add_gap(1007, 1024, 7) \
        .add_gap(1007, 1025, 10) \
        .add_gap(1008, 1009, 15) \
        .add_gap(1008, 1010, 6) \
        .add_gap(1008, 1021, 10) \
        .add_gap(1008, 1022, 1) \
        .add_gap(1008, 1023, 9) \
        .add_gap(1008, 1024, 8) \
        .add_gap(1008, 1025, 13) \
        .add_gap(1009, 1010, 8) \
        .add_gap(1009, 1021, 3) \
        .add_gap(1009, 1022, 13) \
        .add_gap(1009, 1023, 14) \
        .add_gap(1009, 1024, 13) \
        .add_gap(1009, 1025, 1) \
        .add_gap(1010, 1021, 5) \
        .add_gap(1010, 1022, 5) \
        .add_gap(1010, 1023, 6) \
        .add_gap(1010, 1024, 5) \
        .add_gap(1010, 1025, 7) \
        .add_gap(1021, 1022, 9) \
        .add_gap(1021, 1023, 10) \
        .add_gap(1021, 1024, 9) \
        .add_gap(1021, 1025, 2) \
        .add_gap(1022, 1023, 8) \
        .add_gap(1022, 1024, 7) \
        .add_gap(1022, 1025, 11) \
        .add_gap(1023, 1024, 6) \
        .add_gap(1023, 1025, 12) \
        .add_gap(1024, 1025, 12)

    print("Gaps East West Substation")
    print(gaps_east_west)

    gaps_quarry = Gaps(reports.boxes)

    gaps_quarry \
        .add_gap(1000, 1001, ) \
        .add_gap(1000, 1002, ) \
        .add_gap(1000, 1003, ) \
        .add_gap(1000, 1005, ) \
        .add_gap(1000, 1006, ) \
        .add_gap(1000, 1007, ) \
        .add_gap(1000, 1008, ) \
        .add_gap(1000, 1009, ) \
        .add_gap(1000, 1010, ) \
        .add_gap(1000, 1021, ) \
        .add_gap(1000, 1022, ) \
        .add_gap(1000, 1023, ) \
        .add_gap(1000, 1024, ) \
        .add_gap(1000, 1025, ) \
        .add_gap(1001, 1002, ) \
        .add_gap(1001, 1003, ) \
        .add_gap(1001, 1005, ) \
        .add_gap(1001, 1006, ) \
        .add_gap(1001, 1007, ) \
        .add_gap(1001, 1008, ) \
        .add_gap(1001, 1009, ) \
        .add_gap(1001, 1010, ) \
        .add_gap(1001, 1021, ) \
        .add_gap(1001, 1022, ) \
        .add_gap(1001, 1023, ) \
        .add_gap(1001, 1024, ) \
        .add_gap(1001, 1025, ) \
        .add_gap(1002, 1003, ) \
        .add_gap(1002, 1005, ) \
        .add_gap(1002, 1006, ) \
        .add_gap(1002, 1007, ) \
        .add_gap(1002, 1008, ) \
        .add_gap(1002, 1009, ) \
        .add_gap(1002, 1010, ) \
        .add_gap(1002, 1021, ) \
        .add_gap(1002, 1022, ) \
        .add_gap(1002, 1023, ) \
        .add_gap(1002, 1024, ) \
        .add_gap(1002, 1025, ) \
        .add_gap(1003, 1005, ) \
        .add_gap(1003, 1006, ) \
        .add_gap(1003, 1007, ) \
        .add_gap(1003, 1008, ) \
        .add_gap(1003, 1009, ) \
        .add_gap(1003, 1010, ) \
        .add_gap(1003, 1021, ) \
        .add_gap(1003, 1022, ) \
        .add_gap(1003, 1023, ) \
        .add_gap(1003, 1024, ) \
        .add_gap(1003, 1025, ) \
        .add_gap(1005, 1006, ) \
        .add_gap(1005, 1007, ) \
        .add_gap(1005, 1008, ) \
        .add_gap(1005, 1009, ) \
        .add_gap(1005, 1010, ) \
        .add_gap(1005, 1021, ) \
        .add_gap(1005, 1022, ) \
        .add_gap(1005, 1023, ) \
        .add_gap(1005, 1024, ) \
        .add_gap(1005, 1025, ) \
        .add_gap(1006, 1007, ) \
        .add_gap(1006, 1008, ) \
        .add_gap(1006, 1009, ) \
        .add_gap(1006, 1010, ) \
        .add_gap(1006, 1021, ) \
        .add_gap(1006, 1022, ) \
        .add_gap(1006, 1023, ) \
        .add_gap(1006, 1024, ) \
        .add_gap(1006, 1025, ) \
        .add_gap(1007, 1008, ) \
        .add_gap(1007, 1009, ) \
        .add_gap(1007, 1010, ) \
        .add_gap(1007, 1021, ) \
        .add_gap(1007, 1022, ) \
        .add_gap(1007, 1023, ) \
        .add_gap(1007, 1024, ) \
        .add_gap(1007, 1025, ) \
        .add_gap(1008, 1009, ) \
        .add_gap(1008, 1010, ) \
        .add_gap(1008, 1021, ) \
        .add_gap(1008, 1022, ) \
        .add_gap(1008, 1023, ) \
        .add_gap(1008, 1024, ) \
        .add_gap(1008, 1025, ) \
        .add_gap(1009, 1010, ) \
        .add_gap(1009, 1021, ) \
        .add_gap(1009, 1022, ) \
        .add_gap(1009, 1023, ) \
        .add_gap(1009, 1024, ) \
        .add_gap(1009, 1025, ) \
        .add_gap(1010, 1021, ) \
        .add_gap(1010, 1022, ) \
        .add_gap(1010, 1023, ) \
        .add_gap(1010, 1024, ) \
        .add_gap(1010, 1025, ) \
        .add_gap(1021, 1022, ) \
        .add_gap(1021, 1023, ) \
        .add_gap(1021, 1024, ) \
        .add_gap(1021, 1025, ) \
        .add_gap(1022, 1023, ) \
        .add_gap(1022, 1024, ) \
        .add_gap(1022, 1025, ) \
        .add_gap(1023, 1024, ) \
        .add_gap(1023, 1025, ) \
        .add_gap(1024, 1025, )
    print("Gaps Quarry Substation")
    print(gaps_quarry)
