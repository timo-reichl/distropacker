
import getpass

from distropackager import package_root_dir
from distropackager.process import ProcessContext


class BaseImage(object):

    def __init__(self, base):
        self.base = base

    def build(self, tag=0):
        if tag == 0:
            tag = self.next_tag

        image_name = self.with_tag(tag)

        with ProcessContext(
            f"docker build --build-arg user={getpass.getuser()} -t {image_name} .",
            run_dir=self.base.parent,
            print_stdout=True,
        ):
            # we might need the tag later
            return tag

    @property
    def name(self):
        return f"{package_root_dir.name}-{self.base.parent.name}"

    def with_tag(self, tag):
        return f"{self.name}:{tag}"

    @property
    def tag(self):
        with ProcessContext(
                f"docker images {self.name}",
                run_dir=package_root_dir,
                cache_stdout=True
        ) as pc:
            #
            # first line:
            #   REPOSITORY              TAG                 IMAGE ID            CREATED             SIZE
            #
            # last line:
            #   <empty>
            #
            #  >> those can be ignored
            return len(pc.stdout) - 2

    @property
    def next_tag(self):
        return self.tag + 1


class DockerImage(BaseImage):

    def __init__(self, package):
        super().__init__(package_root_dir.parent.joinpath("docker", package.base_name, "Dockerfile"))
