class Track:
    def __init__(self, track_number):
        self.number = track_number

    def __getattr__(self, name):
        return getattr(self.album, name)

class Disk:
    def __init__(self, disk_number):
        self.tracks = {}
        self.number = disk_number

    def track(self, track_number):
        if self.tracks.has_key(track_number):
            return self.tracks[track_number]
        else:
            self.tracks[track_number] = Track(track_number)
            return self.tracks[track_number]

class Album:
    def __init__(self):
        self.disks = {}

    def disk(self, disk_number):
        if self.disks.has_key(disk_number):
            disk = self.disks[disk_number]
        else:
            self.disks[disk_number] = Disk(disk_number)
            disk = self.disks[disk_number]
            disk.number = disk_number
        return disk
