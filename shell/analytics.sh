#!/bin/sh
export PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin
/usr/bin/wget -qN http://analytics.ai7mei.com/history/stat-$(date --date="yesterday"  +'%Y%m%d').log -P /data/stat/analytics && python /data/www/ecp/shell/cron_analytics_handler.py