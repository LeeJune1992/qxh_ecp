-- MySQL dump 10.13  Distrib 5.5.29, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: ai7m
-- ------------------------------------------------------
-- Server version	5.5.29-0ubuntu0.12.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (101,'员工','A,orders,add_order,order_approval,manage_order,edit_order,order_detail,B,my_users,search_user_form,search_user,user,edit_user,add_user,update_address'),(102,'销售内勤','A,orders,order_search,order_approval,manage_order,order_detail,print_order_invoices,C,skus,sku_set_manage,B,search_user_form,search_user,manage_users,user,view_user_phone,sms_list,sms_approval,sms_mass,E,sale_report,sale_report_by_item,financial_report,financial_report_by_dzbb,financial_report_by_paidan,financial_report_by_paidan_tuihuo,financial_report_by_qianshou,financial_report_by_qianshou_tuihuo,logistics_report,logistics_report_by_day_delivery,logistics_report_by_loss,D'),(103,'财务','A,orders,order_search,order_approval,manage_order,order_detail,C,skus,E,financial_report,financial_report_by_sale,financial_report_by_return,financial_report_by_dzbb,financial_report_by_paidan,financial_report_by_paidan_tuihuo,financial_report_by_qianshou,financial_report_by_qianshou_tuihuo,logistics_report,logistics_report_by_day_delivery,logistics_report_by_io,logistics_report_by_loss,D,purchase_price,stock_in_list,stock_in_approval,stock_out_list,stock_out_approval'),(104,'物流','A,orders,order_search,order_approval,manage_order,edit_order,order_detail,print_order_invoices,order_fast_delivery,E,logistics_report,logistics_report_by_day_delivery,logistics_report_by_wlfhhz,logistics_report_by_io,logistics_report_by_loss,D,stock_in_list,add_stock_in,edit_stock_in,stock_out_list,add_stock_out,edit_stock_out,stock_delete'),(105,'物流内勤','A,orders,order_search,order_approval,manage_order,order_detail,E,financial_report,financial_report_by_dzbb'),(106,'销售主管','A,orders,order_search,add_order,order_approval,manage_order,edit_order,order_detail,B,my_users,public_new_users,search_user_form,search_user,manage_users,change_user_op,user,edit_user,add_user,update_address,E,sale_report,sale_report_by_ygxs,sale_report_by_staff,sale_report_by_team,sale_report_by_item,sale_report_by_ygdhtj,sale_report_by_ddxsmxtj,sale_report_by_arrival_detail,sale_report_by_arrival_total,sale_report_by_return_detail,sale_report_by_return_total,D'),(107,'产品管理','C,items,del_item,skus,edit_sku,add_sku,sku_set_manage,add_sku_set,update_sku_set_status,D,stock_in_list,add_stock_in,stock_out_list,add_stock_out'),(999,'系统管理员',NULL),(1000,'第三方商城','A,orders,add_order,order_approval,manage_order,edit_order,order_detail,B,my_users,search_user_form,search_user,user,edit_user,add_user,update_address'),(1001,'分销商','A,orders,add_order,order_approval,manage_order,edit_order,order_detail,B,my_users,search_user_form,search_user,user,edit_user,add_user,update_address'),(1002,'客情','A,orders,add_order,order_approval,manage_order,edit_order,order_detail,B,my_users,search_user_form,search_user,user,edit_user,add_user,update_address'),(1003,'维护主管','A,orders,order_search,add_order,order_approval,manage_order,edit_order,order_detail,except_orders,B,my_users,public_old_users,search_user_form,search_user,manage_users,change_user_op,user,edit_user,add_user,update_address,E,sale_report,sale_report_by_ygxs,sale_report_by_staff,sale_report_by_team,sale_report_by_item,sale_report_by_ygdhtj,sale_report_by_ddxsmxtj,sale_report_by_arrival_detail,sale_report_by_arrival_total,sale_report_by_return_detail,sale_report_by_return_total,D'),(1004,'总经办','A,orders,order_search,order_detail,user,E,sale_report,sale_report_by_ygxs,sale_report_by_staff,sale_report_by_team,sale_report_by_item,sale_report_by_arrival_detail,sale_report_by_arrival_total,financial_report,financial_report_by_sale,financial_report_by_return,financial_report_by_dzbb,logistics_report,logistics_report_by_day_delivery,logistics_report_by_io,logistics_report_by_loss'),(1005,'营销经理','A,orders,order_search,add_order,change_order_op,order_approval,manage_order,edit_order,order_detail,print_order_invoices,except_orders,C,skus,B,my_users,public_new_users,public_old_users,search_user_form,search_user,manage_users,change_user_op,change_user_type,user,edit_user,add_user,update_address,E,sale_report,sale_report_by_ygxs,sale_report_by_staff,sale_report_by_team,sale_report_by_item,sale_report_by_ygdhtj,sale_report_by_ddxsmxtj,sale_report_by_arrival_detail,sale_report_by_arrival_total,sale_report_by_return_detail,sale_report_by_return_total,financial_report,financial_report_by_sale,financial_report_by_return,financial_report_by_dzbb,financial_report_by_paidan,financial_report_by_paidan_tuihuo,financial_report_by_qianshou,financial_report_by_qianshou_tuihuo,logistics_report,logistics_report_by_day_delivery,logistics_report_by_io,logistics_report_by_loss,D,F,manage_news,edit_news,add_news,del_news,operators,edit_operator,add_operator'),(1006,'库房管理','A,orders,order_search,order_detail,C,items,skus,sku_set_manage,add_sku_set,update_sku_set_status,E,financial_report,financial_report_by_paidan,financial_report_by_paidan_tuihuo,financial_report_by_qianshou,financial_report_by_qianshou_tuihuo,logistics_report,logistics_report_by_day_delivery,logistics_report_by_wlfhhz,logistics_report_by_io,logistics_report_by_loss,D,stock_in_list,add_stock_in,edit_stock_in,stock_out_list,add_stock_out,edit_stock_out'),(1007,'媒体专员','E,analytics_report,analytics_report_by_medium,G,product_manage,medium_manage,place_manage,content_list,content_add,content_edit,ad_add,ad_list');
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-09-29 14:18:50
