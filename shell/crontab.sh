#NTP update(cn.pool.ntp.org,time.stdtime.gov.tw)
30  4,16    *   *   *   root /usr/sbin/ntpdate cn.pool.ntp.org;/sbin/hwclock -w;echo "ntp time successful at $(date)." >> /var/log/ntpdate_$(date +\%Y\%m)
30      4       *       *       *       /usr/bin/db_backup.sh >> /var/log/ecp/cron_$(date +\%Y\%m) 2>&1
0      5       *       *       *       /usr/bin/bak_sync.sh >> /var/log/backup_log_$(date +\%Y\%m) 2>&1
5       0       *       *       *       python2.7 /data/www/ecp/shell/cron_cleanup.py >> /var/log/ecp/cron_$(date +\%Y\%m) 2>&1
30      0       *       *       *       python2.7 /data/www/ecp/shell/cron_feihu_stat_handler.py >> /var/log/ecp/cron_$(date +\%Y\%m) 2>&1
30      15       *       *       *       python2.7 /data/www/ecp/shell/cron_bj_feihu_stat_handler.py >> /var/log/ecp/cron_$(date +\%Y\%m) 2>&1
30      1       *       *       *       python2.7 /data/www/ecp/shell/cron_lhyd_stat_handler.py >> /var/log/ecp/cron_$(date +\%Y\%m) 2>&1
40      13       *       *       *       python2.7 /data/www/ecp/shell/cron_xianems_stat_handler.py >> /var/log/ecp/cron_xianems$(date +\%Y\%m) 2>&1
40      13       *       *       *       python2.7 /data/www/ecp/shell/cron_xianems0_stat_handler.py >> /var/log/ecp/cron_xianems0$(date +\%Y\%m) 2>&1
#40      13       *       *       *       python2.7 /data/www/ecptest/shell/cron_xianems0_stat_handler.py >> /var/log/ecptest/cron_xianems0$(date +\%Y\%m) 2>&1
30      15       *       *       *       python2.7 /data/www/ecptest/shell/cron_xianems_stat_handler.py >> /var/log/ecptest/cron_xianems$(date +\%Y\%m) 2>&1
#20      0       *       *       *       python2.7 /data/www/ecp/shell/cron_deliver_stat_handler.py >> /var/log/ecp/cron_$(date +\%Y\%m) 2>&1
*/1     9-23    *       *       *       python2.7 /data/www/ecp/shell/cron_order_assign_scheduler.py >> /var/log/ecp/cron_$(date +\%Y\%m) 2>&1
*/1     0-23    *       *       *       python2.7 /data/www/ecp/shell/cron_per_minute_scheduler.py >> /var/log/ecp/cron_$(date +\%Y\%m) 2>&1
*/1     0-23    *       *       *       python2.7 /data/www/ecp/manage.py sendSMS >> /var/log/ecp/cron_test_$(date +\%Y\%m) 2>&1
#10      0       *       *       *       python2.7 /data/www/ecptest/shell/cron_cleanup.py >> /var/log/ecp/cron_test_$(date +\%Y\%m) 2>&1
*/1     9-23    *       *       *       python2.7 /data/www/ecptest/shell/cron_order_assign_scheduler.py >> /var/log/ecp/cron_test_$(date +\%Y\%m) 2>&1
*/1     0-23    *       *       *       python2.7 /data/www/ecptest/shell/cron_per_minute_scheduler.py >> /var/log/ecp/cron_test_$(date +\%Y\%m) 2>&1
#*/1     0-23    *       *       *       python2.7 /data/www/ecptest/manage.py sendSMS >> /var/log/ecp/cron_test_$(date +\%Y\%m) 2>&1
50      0       *       *       *       /usr/bin/wget -qN http://analytics.ai7mei.com/history/stat-$(date --date="yesterday"  +'%Y%m%d').log -P /data/stat/analytics && python /data/www/ecp/shell/cron_analytics_handler.py  >> /var/log/ecp/cron_$(date +\%Y\%m) 2>&1
#30      2       *       *       *       python /data/www/ecp/shell/cron_analytics_handler.py >> /var/log/ecp/cron_$(date +\%Y\%m) 2>&1
#
30     23    *       *       *       python2.7 /data/www/ecp/shell/cron_user_statistics_handler.py >> /var/log/ecp/cron_user_statistics_$(date +\%Y\%m) 2>&1
30     23    *       *       *       python2.7 /data/www/ecptest/shell/cron_user_statistics_handler.py >> /var/log/ecptest/cron_user_statistics_$(date +\%Y\%m) 2>&1