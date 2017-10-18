import os

from conans import ConanFile, tools

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

class BoostConan(ConanFile):
    name = "boost"
    version = "1.65.1"
    description = "boost"
    license="Boost Software License - Version 1.0. http://www.boost.org/LICENSE_1_0.txt"
    url = "https://github.com/dsiroky/conan-boost"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    FOLDER_NAME = "boost_%s" % version.replace(".", "_")

    exports_sources = [FOLDER_NAME + "*"]
    no_copy_source = True

    def build(self):
        self.bootstrap()
        self.b2()

    def bootstrap(self):
        command = "bootstrap.bat" if self.settings.os == "Windows" else "./bootstrap.sh"
        self.run("cd %s && cd %s && %s" % (self.source_folder, self.FOLDER_NAME, command))

    def b2(self):
        flags = []
        flags += ["-j%i" % tools.cpu_count()]
        flags += ["link=static", "threading=multi", "address-model=64"]
        flags += [
                    "--stagedir=%s" % os.path.join(self.build_folder, "stage"),
                    "--build-dir=%s" % os.path.join(self.build_folder, "build")
                ]
        if self.settings.os == "Windows":
            flags += ["variant=debug,release", "runtime-link=shared,static"]
        flags += ["stage"]

        command = "cd %s && cd %s" % (self.source_folder, self.FOLDER_NAME)
        if self.settings.os == "Windows":
            command += " && b2"
        else:
            command += " && ./b2"
        self.run(command + " " + " ".join(flags))

    def package(self):
        self.copy(pattern="*", dst="include/boost", src="%s/%s/boost" % (self.source_folder, self.FOLDER_NAME))
        self.copy(pattern="*.a", dst="lib", src="%s/stage/lib" % self.build_folder)
        self.copy(pattern="*.so", dst="lib", src="%s/stage/lib" % self.build_folder)
        self.copy(pattern="*.so.*", dst="lib", src="%s/stage/lib" % self.build_folder)
        self.copy(pattern="*.dylib*", dst="lib", src="%s/stage/lib" % self.build_folder)
        self.copy(pattern="*.lib", dst="lib", src="%s/stage/lib" % self.build_folder)
        self.copy(pattern="*.dll", dst="bin", src="%s/stage/lib" % self.build_folder)

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
