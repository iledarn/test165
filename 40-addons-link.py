import logging
import os
import yaml
from glob import glob
from glob import iglob

LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})

CUSTOM_DIR = "/home/ildar/TEST165"
AUTO_DIR = "/home/ildar/TEST165/auto"
ADDONS_DIR = os.path.join(AUTO_DIR, "addons")
SRC_DIR = CUSTOM_DIR


ADDONS_YAML = os.path.join(CUSTOM_DIR, "addons.yaml")

PRIVATE = "private"
CORE = "odoo/addons"

PRIVATE_DIR = os.path.join(SRC_DIR, PRIVATE)
CORE_DIR = os.path.join(SRC_DIR, CORE)

ODOO_DIR = os.path.join(SRC_DIR, "odoo")

ODOO_VERSION = 16.0

MANIFESTS = ("__manifest__.py", "__openerp__.py")

# Customize logging for build
logger = logging.getLogger("doodba")
log_handler = logging.StreamHandler()
log_formatter = logging.Formatter("%(name)s %(levelname)s: %(message)s")
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)
_log_level = os.environ.get("LOG_LEVEL", "")
if _log_level.isdigit():
    _log_level = int(_log_level)
elif _log_level in LOG_LEVELS:
    _log_level = getattr(logging, _log_level)
else:
    if _log_level:
        logger.warning("Wrong value in $LOG_LEVEL, falling back to INFO")
    _log_level = logging.INFO
logger.setLevel(_log_level)

logger.info("SRC_DIR %s", SRC_DIR)

class AddonsConfigError(Exception):
    def __init__(self, message, *args):
        super(AddonsConfigError, self).__init__(message, *args)
        self.message = message


def addons_config(filtered=True, strict=False):
    """Yield addon name and path from ``ADDONS_YAML``.

    :param bool filtered:
        Use ``False`` to include all addon definitions. Use ``True`` (default)
        to include only those matched by ``ONLY`` clauses, if any.

    :param bool strict:
        Use ``True`` to raise an exception if any declared addon is not found.

    :return Iterator[str, str]:
        A generator that yields ``(addon, repo)`` pairs.
    """
    config = dict()
    missing_glob = set()
    missing_manifest = set()
    all_globs = {}

    try:
        with open(ADDONS_YAML) as addons_file:
            for doc in yaml.safe_load_all(addons_file):
                # Skip sections with ONLY and that don't match
                only = doc.pop("ONLY", {})
                if not filtered:
                    doc.setdefault(CORE, ["*"])
                    doc.setdefault(PRIVATE, ["*"])
                elif any(
                    os.environ.get(key) not in values for key, values in only.items()
                ):
                    continue
                # Flatten all sections in a single dict
                for repo, partial_globs in doc.items():
                    if repo == "ENV":
                        continue
                    all_globs.setdefault(repo, set())
                    all_globs[repo].update(partial_globs)
    except IOError:
        logger.debug("Could not find addons configuration yaml.")

    print("all_globs: ", all_globs)

    for repo in (CORE, PRIVATE):
        all_globs.setdefault(repo, {"*"})

    for repo, partial_globs in all_globs.items():
        for partial_glob in partial_globs:
            full_glob = os.path.join(SRC_DIR, repo, partial_glob)
            print(full_glob)
            found = glob(full_glob)
            # print(found)

            for addon in found:
                if not os.path.isdir(addon):
                    continue
                manifests = (os.path.join(addon, m) for m in MANIFESTS)
                if not any(os.path.isfile(m) for m in manifests):
                    missing_manifest.add(addon)
                    logger.debug(
                        "Skipping '%s' as it is not a valid Odoo " "module", addon
                    )
                    continue
                logger.debug("Registering addon %s", addon)
                addon = os.path.basename(addon)
                config.setdefault(addon, set())
                config[addon].add(repo)

    for addon, repos in config.items():
        # Private addons are most important
        if PRIVATE in repos:
            yield addon, PRIVATE
            continue
        # Odoo core addons are least important
        if repos == {CORE}:
            yield addon, CORE
            continue
        repos.discard(CORE)
        # Other addons fall in between
        if filtered and len(repos) != 1:
            raise AddonsConfigError(
                "Addon {} defined in several repos {}".format(addon, repos)
            )
        for repo in repos:
            yield addon, repo


logger.info("Linking all addons from %s in %s", ADDONS_YAML, ADDONS_DIR)

# Remove all links in addons dir
for link in iglob(os.path.join(ADDONS_DIR, "*")):
    os.remove(link)
# Add new links
for addon, repo in addons_config():
    src = os.path.relpath(os.path.join(SRC_DIR, repo, addon), ADDONS_DIR)
    dst = os.path.join(ADDONS_DIR, addon)
    logger.info("src: %s; dst: %s", src, dst)
    os.symlink(src, dst)
    logger.debug("Linked %s in %s", src, dst)
