
import getpass

from distropackager import root_dir
from distropackager.process import ProcessContext


class DockerImage(object):

    def __init__(self, package):
        self.package = package
        self.dockerfile = root_dir.parent.joinpath("docker", package.base_name, "Dockerfile")

    def generate_dockerfile(self, docker_base, user, dependencies, groupadd_string, useradd_string):
        with self.dockerfile.with_suffix(".in").open("r") as dockerfile_in_f:
            dockerfile_contents = dockerfile_in_f.read()

        with self.dockerfile.open("w") as dockerfile_f:
            dockerfile_f.write(dockerfile_contents.format(**{
                "docker_base": docker_base,
                "user": user,
                "dependencies": ' '.join(dependencies) if dependencies else "",
                "groupadd": groupadd_string if groupadd_string else "\\",
                "useradd": useradd_string if useradd_string else "\\"
            }))

    def build(self, dependencies, tag=None, force=False):
        user = getpass.getuser()

        latest = self.latest

        if tag is None:
            tag = latest

        if tag > latest:
            tag = latest

        if tag == 0:
            tag += 1
            force = True

        image_name = self.with_tag(tag)

        # Remove image if we want a clean state for that tag
        if force:
            ProcessContext.execute(
                f"docker image rm {image_name}",
                run_dir=root_dir,
                print_stdout=True
            )

        if force:
            if tag != latest:
                docker_base = self.with_tag(self.package.docker_base_tag, self.package.docker_base)
                groupadd_string = "groupadd wheel && \\"
                useradd_string = f"useradd -g wheel -d /distropackager {user} && \\"

                # Generate a Dockerfile.in from Dockerfile.in.in
                self.generate_dockerfile(docker_base, user, dependencies, groupadd_string, useradd_string)

            ProcessContext.execute(
                f"docker build -t {image_name} .",
                run_dir=self.dockerfile.parent,
                print_stdout=True
            )

            return tag

    @property
    def images_available(self):
        #
        # first line:
        #   REPOSITORY              TAG                 IMAGE ID            CREATED             SIZE
        #
        # last line:
        #   <empty>
        #
        #  >> those can be ignored
        return ProcessContext.execute(
            f"docker images {self.name}",
            run_dir=root_dir,
            cache_stdout=True
        ).stdout[1:-1]

    @property
    def latest(self):
        return len(self.images_available)

    @property
    def name(self):
        return f"{root_dir.name}-{self.dockerfile.parent.name}"

    def with_tag(self, tag, name=None):
        return f"{name if name is not None else self.name}:{tag}"
