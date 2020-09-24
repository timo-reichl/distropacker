from distropackager import samples_dir
from distropackager.package import package_manager


package = package_manager.get("Manjaro", samples_dir.joinpath("arch"))
package.build([])
