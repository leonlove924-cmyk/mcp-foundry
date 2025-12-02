import importlib
import importlib.util
import os
import logging
import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("azure-ai-foundry-mcp-server")

logger = logging.getLogger(__name__)

def auto_import_modules(base_package: str, targets: list[str]):
    """
    Automatically imports specified Python modules (e.g., tools.py, resources.py, prompts.py)
    from each subpackage of base_package.

    This function iterates through all subdirectories of the base package and attempts to import
    the specified target modules (e.g., tools, resources, prompts) from each subpackage.

    Args:
        base_package: The base package name to search for subpackages (e.g., "mcp_foundry")
        targets: List of module names to import from each subpackage (e.g., ["tools", "resources", "prompts"])
    """
    package = importlib.import_module(base_package)
    package_path = package.__path__[0]

    for submodule in os.listdir(package_path):
        sub_path = os.path.join(package_path, submodule)

        if not os.path.isdir(sub_path) or submodule.startswith("__"):
            continue

        for target in targets:
            module_name = f"{base_package}.{submodule}.{target}"
            module_file = os.path.join(sub_path, f"{target}.py")

            # Check if the module file exists before attempting to import
            if not os.path.isfile(module_file):
                logger.debug(f"⏭️ Skipping {module_name} (file does not exist)")
                continue

            try:
                importlib.import_module(module_name)
                logger.info(f"✅ Imported: {module_name}")
            except ModuleNotFoundError as e:
                # Module file exists but has missing dependencies
                logger.error(f"❌ Error importing {module_name}: missing dependency - {e}")
            except Exception as e:
                logger.error(f"❌ Error importing {module_name}: {e}")
 