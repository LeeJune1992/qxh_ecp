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
-- Dumping data for table `address`
--

LOCK TABLES `address` WRITE;
/*!40000 ALTER TABLE `address` DISABLE KEYS */;
/*!40000 ALTER TABLE `address` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `china_address`
--

LOCK TABLES `china_address` WRITE;
/*!40000 ALTER TABLE `china_address` DISABLE KEYS */;
/*!40000 ALTER TABLE `china_address` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `item`
--

LOCK TABLES `item` WRITE;
/*!40000 ALTER TABLE `item` DISABLE KEYS */;
INSERT INTO `item` (`id`, `name`, `category_id`, `desc`, `status`) VALUES (1,'保健品',1,'',1),(2,'气血和胶囊',3,'',1),(3,'芪枣健胃茶',3,'',1),(4,'气·祛痘调理系列',2,'',1),(5,'雪·美白淡斑系列',2,'',1),(6,'和·抗皱补水系列',2,'',1),(7,'原液',2,'',1),(8,'面膜',2,'',1),(9,'赠品',9,'',1);
/*!40000 ALTER TABLE `item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `news`
--

LOCK TABLES `news` WRITE;
/*!40000 ALTER TABLE `news` DISABLE KEYS */;
/*!40000 ALTER TABLE `news` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `operator`
--

LOCK TABLES `operator` WRITE;
/*!40000 ALTER TABLE `operator` DISABLE KEYS */;
INSERT INTO `operator` (`id`, `nickname`, `email`, `username`, `password`, `created`, `role_id`, `is_admin`, `assign_orders`, `status`) VALUES (1,'管理员',NULL,'ai7m','sha1$uM1tfOK1$5e91065368fbecb6008c4e82a34f5387ca7fd03d','2013-03-26 14:05:09',0,1,0,2),(2,'王芸','test@test.com','wangyun','sha1$jnDwd7xE$fd1d9dc2e6e79af0e096cd0b53e6bd0a5d158661','2013-03-26 14:06:50',32,0,0,2);
/*!40000 ALTER TABLE `operator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `order`
--

LOCK TABLES `order` WRITE;
/*!40000 ALTER TABLE `order` DISABLE KEYS */;
/*!40000 ALTER TABLE `order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `order_item`
--

LOCK TABLES `order_item` WRITE;
/*!40000 ALTER TABLE `order_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `order_log`
--

LOCK TABLES `order_log` WRITE;
/*!40000 ALTER TABLE `order_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `order_sets`
--

LOCK TABLES `order_sets` WRITE;
/*!40000 ALTER TABLE `order_sets` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_sets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `sku`
--

LOCK TABLES `sku` WRITE;
/*!40000 ALTER TABLE `sku` DISABLE KEYS */;
INSERT INTO `sku` (`id`, `item_id`, `name`, `properties`, `unit`, `code`, `price`, `market_price`, `discount_price`, `quantity`, `order_quantity`, `loss_quantity`, `threshold`, `warning_threshold`, `created`, `modified`, `status`) VALUES (10001,2,'气血和胶囊（小盒）','p2:u\"盒\",p3:u\"胶囊\",p1:u\"36粒\"','盒','6923009809587',49,49,0,0,0,0,100,400,'2013-03-26 14:28:54','2013-03-26 14:28:54',1),(10002,2,'气血和胶囊（中盒）','p2:u\"盒\",p3:u\"胶囊\",p1:u\"144粒\"','盒','6923009809556',188,188,0,0,0,0,300,1100,'2013-03-26 14:31:13','2013-03-26 14:31:13',1),(10003,2,'气血和胶囊（大盒）','p2:u\"盒\",p3:u\"胶囊\",p1:u\"216粒\"','盒','6923009809662',268,268,0,0,0,0,300,1100,'2013-03-26 14:31:50','2013-03-26 14:31:50',1),(10004,3,'芪枣健胃茶','p2:u\"盒\",p3:u\"茶剂\",p1:u\"5g*6袋\"','盒','6941057281933',29.8,29.8,0,0,0,0,800,2800,'2013-03-26 14:32:50','2013-03-26 14:32:50',1),(10005,6,'和.津水回颜抗皱套盒','p2:u\"套\",p3:u\"溶液\",p1:u\"一套\"','盒','6949073188700',580,860,0,0,0,0,150,500,'2013-03-26 14:37:39','2013-03-26 14:37:39',1),(10006,6,'和.津水回颜水凝霜','p1:u\"50g\"','瓶','6949073188588',166,216,0,0,0,0,150,400,'2013-03-26 14:39:44','2013-03-26 14:39:44',1),(10007,6,'和.津水明眸多效眼霜','p1:u\"30g\"','瓶','6949073188595',298,386,0,0,0,0,100,300,'2013-03-26 14:42:38','2013-03-26 14:42:38',1),(10008,5,'雪.白肌活源美白淡斑套盒','p2:u\"套\",p3:u\"溶液\",p1:u\"一套\"','盒','6949073188717',1100,1700,0,0,0,0,150,500,'2013-03-26 14:45:25','2013-03-26 14:45:25',1),(10009,5,'雪.白肌活源抽色霜','p1:u\"30g\"','瓶','6949073188649',240,312,0,0,0,0,100,300,'2013-03-26 14:47:24','2013-03-26 14:47:24',1),(10010,5,'雪.白肌活源洗面奶','p1:u\"120ml\"','盒','6949073188601',152,196,0,0,0,0,100,300,'2013-03-26 14:49:27','2013-03-26 14:49:27',1),(10011,5,'雪.白肌活源爽肤水','p1:u\"120ml\"','瓶','6949073188618',198,258,0,0,0,0,100,300,'2013-03-26 14:51:15','2013-03-26 14:51:15',1),(10012,5,'雪.白肌活源魔焕BB霜','p1:u\"50g\"','盒','6949073188656',199,258,0,0,0,0,150,600,'2013-03-26 14:52:03','2013-03-26 14:52:03',1),(10013,5,'雪.白肌活源精华素','p1:u\"30ml\"','盒','6949073188625',206,268,0,0,0,0,150,500,'2013-03-26 14:53:47','2013-03-26 14:53:47',1),(10014,4,'气清安肤.祛痘无痕套盒','p1:u\"一套\"','盒','6949073188694',580,860,0,0,0,0,100,300,'2013-03-26 14:55:51','2013-03-26 14:55:51',1),(10015,4,'气清安肤.控油水','p1:u\"120ml\"','瓶','6949073188663',168,198,0,0,0,0,100,300,'2013-03-26 14:56:49','2013-03-26 14:56:49',1),(10016,4,'气清安肤.祛痘印精华','p1:u\"30ml\"','瓶','6949073188670',298,398,0,0,0,0,150,500,'2013-03-26 14:58:09','2013-03-26 14:58:09',1),(10017,7,'洋甘菊舒敏(原液)','p1:u\"10ml\"','瓶','6949073188526',248,322,0,0,0,0,150,600,'2013-03-26 15:02:47','2013-03-26 15:02:47',1),(10018,7,'玻尿酸锁水(原液)','p1:u\"10ml\"','瓶','6949073188502',306,398,0,0,0,0,150,600,'2013-03-26 15:03:33','2013-03-26 15:03:33',1),(10019,7,'瞬间扶纹抗皱(原液)','p1:u\"10ml\"','瓶','6949073188519',282,368,0,0,0,0,150,600,'2013-03-26 15:04:40','2013-03-26 15:04:40',1),(10020,7,'红石榴抗衰(原液)','p1:u\"10ml\"','瓶','6949073188533',245,318,0,0,0,0,150,600,'2013-03-26 15:05:18','2013-03-26 15:05:18',1),(10021,1,'珍美软胶囊','p2:u\"瓶\",p3:u\"胶囊\",p1:u\"100粒\"','瓶','6909782886915',238,398,0,0,0,0,190,500,'2013-03-26 15:08:54','2013-03-26 15:08:54',1),(10022,1,'辅酶Q10维E软胶囊','p2:u\"瓶\",p3:u\"胶囊\",p1:u\"60粒\"','瓶','6909782886861',162,268,0,0,0,0,150,400,'2013-03-26 15:11:45','2013-03-26 15:11:45',1),(10023,1,'羊胚胎胶囊','p2:u\"瓶\",p3:u\"胶囊\",p1:u\"60粒\"','瓶','6909782886908',178,298,0,0,0,0,190,500,'2013-03-26 15:19:35','2013-03-26 15:19:35',1),(10024,1,'大豆提取物胶原蛋白胶囊','p2:u\"瓶\",p3:u\"胶囊\",p1:u\"60粒\"','瓶','6924217125261',68,108,0,0,0,0,190,500,'2013-03-26 15:21:03','2013-03-26 15:21:03',1),(10025,1,'天然维生素E硒软胶囊','p2:u\"瓶\",p3:u\"胶囊\",p1:u\"60粒\"','瓶','6924217125285',178,298,0,0,0,0,100,300,'2013-03-26 15:22:08','2013-03-26 15:22:08',1),(10026,1,'β-胡萝卜素软胶囊','p2:u\"瓶\",p3:u\"胶囊\",p1:u\"100粒\"','瓶','6909782886885',162,268,0,0,0,0,100,300,'2013-03-26 15:23:01','2013-03-26 15:23:01',1),(10027,1,'多种维生素矿物质片','p2:u\"瓶\",p3:u\"片状\",p1:u\"60片\"','瓶','6924217125292',78,128,0,0,0,0,100,300,'2013-03-26 15:24:24','2013-03-26 15:24:24',1),(10028,1,'葡萄籽芦荟软胶胶囊','p2:u\"瓶\",p3:u\"胶囊\",p1:u\"60粒\"','瓶','6924217125278',118,198,0,0,0,0,190,500,'2013-03-26 15:25:08','2013-03-26 15:25:08',1),(10029,1,'木瓜葛根压片糖果','p2:u\"瓶\",p3:u\"片状\",p1:u\"100片\"','瓶','6924217125254',178,298,0,0,0,0,150,400,'2013-03-26 15:26:44','2013-03-26 15:26:44',1),(10030,8,'沁颜补水清润面膜','p2:u\"盒\",p3:u\"片状\",p1:u\"30ml*2片\"','盒','6949073191007',38,49,0,0,0,0,330,1100,'2013-03-26 15:29:10','2013-03-26 15:29:10',1),(10031,9,'爱妻美暖宫贴（非卖品）','p1:u\"2贴/盒\"','盒','6949327500012',0,49,0,0,0,0,150,400,'2013-03-26 15:42:14','2013-03-26 15:42:14',1),(10032,9,'军之贡足贴','p1:u\"10贴/盒\"','盒','6948625200068',0,128,0,0,0,0,400,1300,'2013-03-26 15:42:59','2013-03-26 15:42:59',1),(10033,9,'魔力挺','p1:u\"1套/盒\"','盒','6945727182131',0,298,0,0,0,0,200,900,'2013-03-26 15:43:44','2013-03-26 15:43:44',1);
/*!40000 ALTER TABLE `sku` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `sku_set`
--

LOCK TABLES `sku_set` WRITE;
/*!40000 ALTER TABLE `sku_set` DISABLE KEYS */;
INSERT INTO `sku_set` (`id`, `name`, `config`, `price`, `is_valid`, `created`) VALUES (1001,'美白经典装','10024:1,10018:1,10013:1,10021:1',536,0,'2013-03-26 16:03:06'),(1002,'美白焕颜装','10018:1,10013:1,10021:1',416,0,'2013-03-26 16:04:08'),(1004,'抗衰经典装','10020:1,10028:1,10006:1,10023:1',612,0,'2013-03-26 16:07:07'),(1005,'抗衰焕颜装 ','10020:1,10006:1,10023:1',498,0,'2013-03-26 16:07:51'),(1006,'抗衰基础装','10020:1,10023:1',298,0,'2013-03-26 16:08:20'),(1007,'美白基础装','10018:1,10021:1',198,1,'2013-03-26 16:18:57');
/*!40000 ALTER TABLE `sku_set` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `stock`
--

LOCK TABLES `stock` WRITE;
/*!40000 ALTER TABLE `stock` DISABLE KEYS */;
/*!40000 ALTER TABLE `stock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `store`
--

LOCK TABLES `store` WRITE;
/*!40000 ALTER TABLE `store` DISABLE KEYS */;
/*!40000 ALTER TABLE `store` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-03-26 16:29:56
