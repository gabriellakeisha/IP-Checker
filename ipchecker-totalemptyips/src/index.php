<?php
header("Access-Control-Allow-Origin: *");
header("Content-type: application/json");
require('functions.inc.php');

$output = array(
	"error" => false,
  "items" => "",
	"total_empty_ips" => 0
);

$items = $_REQUEST['items'];
$total_empty_ips=getTotalEmptyIPs($items);

$output['items']=$items;
$output['total_empty_ips']=$total_empty_ips;

echo json_encode($output);
exit();
