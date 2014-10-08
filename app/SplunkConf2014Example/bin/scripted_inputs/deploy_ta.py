from distutils.version import LooseVersion
import distutils.dir_util as dir_util
import logging
import logging.handlers
import os
import sys
import re
from pprint import pprint

import splunk
import splunk.entity
import splunk.appserver.mrsparkle.lib.util as app_util

SPLUNK_HOME = os.environ.get('SPLUNK_HOME')
INSTALLER_LOG_FILENAME = os.path.join(SPLUNK_HOME,'var','log','splunk','ta_installer.log')
logger = logging.getLogger('ta_installer')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(INSTALLER_LOG_FILENAME, maxBytes=1024000, backupCount=5)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

APP_NAME = 'SplunkConf2014Example'
APPS_DIR = app_util.get_apps_dir()
(ETC_DIR, APPS_STEM) = os.path.split(APPS_DIR)
DEPLOYMENT_APPS_DIR = os.path.join(ETC_DIR, 'deployment-apps')
INSTALL_DIR = os.path.join(APPS_DIR, APP_NAME, 'appserver', 'addons')
SPLUNK_PROTOCOL = 'http'
SPLUNK_HOST = 'localhost'
SPLUNK_PORT = '8000'
SPLUNK_ROOT_ENDPOINT = '/'
DEPENDENCIES = ['TA_SplunkConf2014Example']

def create_inputs(appdir, disabled):
    localdir = os.path.join(appdir, 'local')
    if not os.path.exists(localdir):
        os.makedirs(localdir)
    inputs_file = os.path.join(localdir, 'inputs.conf')
    fo = open(inputs_file, 'w')
    fo.write( "#[stanza]\n")
    fo.write( "#connection_host = dns\n")
    fo.write( "#sourcetype = some_sourcetype\n")
    fo.write( "#index = some_index\n")
    fo.write( "#disabled = %d\n" % disabled)
    
    fo.close()
    logger.info("created config file (disabled=%d): %s" % (disabled, inputs_file)) 

def install_dependency(dep):
    src = os.path.join(INSTALL_DIR, dep)
    dst = os.path.join(APPS_DIR, dep)
    try:
        dir_util.copy_tree(src, dst)
        logger.info("%s was successfully copied to %s" % (src, dst)) 
        if (dep == "TA_SplunkConf2014Example"):
            create_inputs(dst, 0)
        if os.path.exists(DEPLOYMENT_APPS_DIR):
            dst = os.path.join(DEPLOYMENT_APPS_DIR, dep)
            dir_util.copy_tree(src, dst)
            logger.info("%s was successfully copied to %s" % (src, dst)) 
            if (dep == "TA_SplunkConf2014Example"):
                create_inputs(dst, 0)
            
    except Exception, ex:
        logger.error("unable to copy %s to %s" % (src, dst)) 
        logger.exception(ex)

def get_loose_version(version, build):
	pattern = re.compile('(\d+\.\d+).*')
	m = pattern.match(version)
	if m:
		version = m.group(1)
	version = "%s build %s" % (version, build)
	return LooseVersion(version)

if __name__ == '__main__':

    token = sys.stdin.readlines()[0]
    token = token.strip()

    logger.info("Splunk .conf 2014 Example App Dependency Manager: Starting...")
   
    en = splunk.entity.getEntity('server/settings', 'settings', sessionKey=token)
    if (en):
        SPLUNK_PROTOCOL = ("https" if int(en['enableSplunkWebSSL'])==1 else "http")
        SPLUNK_HOST = en['host']
        SPLUNK_PORT = en['httpport']
    else:
        logger.error("unable to retrieve server settings")

    en = splunk.entity.getEntity('configs/conf-web', 'settings', sessionKey=token)
    if (en and 'root_endpoint' in en):
        SPLUNK_ROOT_ENDPOINT = en['root_endpoint']
        if not SPLUNK_ROOT_ENDPOINT.startswith('/'):
            SPLUNK_ROOT_ENDPOINT = "/" + SPLUNK_ROOT_ENDPOINT
        if not SPLUNK_ROOT_ENDPOINT.endswith('/'):
            SPLUNK_ROOT_ENDPOINT += '/'
    else:
        logger.error("unable to retrieve root_endpoint setting")

    en = splunk.entity.getEntities('/apps/local', sessionKey=token)
    keys = en.keys()
    version = get_loose_version(en[APP_NAME]['version'], en[APP_NAME]['build'])

    for dep in DEPENDENCIES:
        if not dep in keys:
            logger.info("dependency %s not found - installing..." % dep)
            install_dependency(dep)
        else:
            dep_version = get_loose_version(en[dep]['version'], en[dep]['build'])
            if version > dep_version:
                logger.info("installed version of %s is %s, which is older than required version %s - updating..." % (dep, dep_version, version))
                install_dependency(dep)
            else:
                logger.info("installed version of %s is %s, which is newer or equal to version %s - leaving alone..." % (dep, dep_version, version))

    logger.info("Splunk .conf 2014 Example App Dependency Manager: Exiting...") 
      
