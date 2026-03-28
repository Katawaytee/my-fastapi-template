CREATE TABLE `reservation` (
  `reservation_id` tinyint(4) unsigned NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(255) DEFAULT NULL,
  `table_id` tinyint(4) unsigned DEFAULT NULL,
  `reservation_time` datetime DEFAULT NULL,
  `party_size` tinyint(4) DEFAULT NULL,
  `create_time` datetime NOT NULL DEFAULT current_timestamp(),
  `update_time` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`reservation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;