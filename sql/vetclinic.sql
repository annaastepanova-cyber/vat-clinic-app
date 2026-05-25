

CREATE TABLE `clients` (
  `client_id` int(11) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL
) 


INSERT INTO `clients` (`client_id`, `first_name`, `last_name`, `phone`, `email`) VALUES
(1, 'Иванов', 'Иван', '8963453636', 'ivanov@mail.ru'),
(2, 'Петрова', 'Ольга', '8963453637', 'petrova@mail.ru'),
(3, 'Семенов', 'Андрей', '8963453667', 'semenov@ya.ru'),
(4, 'Кошкин', 'Павел', '8963453669', 'Koshkin@ya.ru');





CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL,
  `client_id` int(11) NOT NULL,
  `veterinar_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `order_date` date NOT NULL,
  `start_time` int(11) NOT NULL,
  `end_time` int(11) NOT NULL,
  `comment` text NOT NULL
)


INSERT INTO `orders` (`order_id`, `client_id`, `veterinar_id`, `service_id`, `order_date`, `start_time`, `end_time`, `comment`) VALUES
(1, 1, 1, 1, '2026-05-01', 10, 11, 'Кошка 3 года'),
(2, 2, 2, 2, '2026-05-01', 11, 12, 'Собака 3 месяца'),
(3, 3, 3, 4, '2026-05-01', 12, 13, 'Собака после прогулки'),
(4, 4, 4, 3, '2026-05-01', 12, 13, 'Прививка от столбняка');



CREATE TABLE `revies` (
  `review_id` int(11) NOT NULL,
  `client_id` int(11) NOT NULL,
  `veterinar_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `raiting` int(11) NOT NULL,
  `comment` varchar(250) NOT NULL
)
INSERT INTO `revies` (`review_id`, `client_id`, `veterinar_id`, `order_id`, `raiting`, `comment`) VALUES
(1, 1, 1, 1, 10, 'Все прошло замечательно'),
(2, 2, 2, 2, 7, 'Понравилось'),
(3, 3, 3, 3, 10, 'собака довольна'),
(4, 4, 4, 4, 3, 'Доктор опоздал');





CREATE TABLE `roles` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL
) 


INSERT INTO `roles` (`id`, `name`, `password`) VALUES
(1, 'doc', '123456'),
(2, 'Клиент', '0000'),
(3, 'директор', '1111'),
(4, 'Admin', '1234');





CREATE TABLE `services` (
  `service_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` varchar(100) NOT NULL,
  `price` int(11) NOT NULL
) 
INSERT INTO `services` (`service_id`, `name`, `description`, `price`) VALUES
(1, 'Чистка ушей', 'Чистка ушей кошкам, собакам', 1000),
(2, 'Стрижка когтей', 'Стрижка когтей собакам, кошкам', 2000),
(3, 'Прививка', 'Прививка собакам, кошкам', 3000),
(4, 'Удаление занозы', 'Удаление занозы из лапы', 4000);



CREATE TABLE `veterinars` (
  `veterinar_id` int(11) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `specialozation` varchar(100) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL
)
INSERT INTO `veterinars` (`veterinar_id`, `first_name`, `last_name`, `specialozation`, `phone`, `email`) VALUES
(1, 'Рыбаков', 'Андрей', 'Хирург', '8963453645', 'rybakov@ya.ru'),
(2, 'Собакин', 'Сергей', 'Терапевт', '8963453645', 'sobakin@mail.ru'),
(3, 'Овчаренко', 'Андрей', 'Хирург', '896345443', 'ovv@ya.ru'),
(4, 'мышкин', 'Сергей', 'Терапевт', '8963453612', 'MNB@mail.ru');

-


ALTER TABLE `clients`
  ADD PRIMARY KEY (`client_id`);

-

ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `client_id` (`client_id`),
  ADD KEY `service_id` (`service_id`),
  ADD KEY `veterinar_id` (`veterinar_id`);



ALTER TABLE `revies`
  ADD PRIMARY KEY (`review_id`),
  ADD KEY `client_id` (`client_id`),
  ADD KEY `veterinar_id` (`veterinar_id`),
  ADD KEY `order_id` (`order_id`);

ALTER TABLE `roles`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `services`
  ADD PRIMARY KEY (`service_id`)
ALTER TABLE `veterinars`
  ADD PRIMARY KEY (`veterinar_id`);




ALTER TABLE `clients`
  MODIFY `client_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;


ALTER TABLE `orders`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;


ALTER TABLE `revies`
  MODIFY `review_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;


ALTER TABLE `roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;



ALTER TABLE `services`
  MODIFY `service_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5
ALTER TABLE `veterinars`
  MODIFY `veterinar_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;



ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`client_id`),
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`service_id`) REFERENCES `services` (`service_id`),
  ADD CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`veterinar_id`) REFERENCES `veterinars` (`veterinar_id`);



ALTER TABLE `revies`
  ADD CONSTRAINT `revies_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`client_id`),
  ADD CONSTRAINT `revies_ibfk_2` FOREIGN KEY (`veterinar_id`) REFERENCES `veterinars` (`veterinar_id`),
  ADD CONSTRAINT `revies_ibfk_3` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`);


COMMIT
