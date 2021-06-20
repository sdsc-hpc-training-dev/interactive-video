<?php

$res = array();
$res['list'] = array();
foreach (glob("./*/config.json") as $filename) {
    $config = file_get_contents($filename);
    $json = json_decode($config, true);
    $obj = array();
    $obj['path'] = explode("/", $filename)[1];
    $obj['title'] = $json['title'];
    $obj['subtitle'] = $json['subtitle'];
    $obj['description'] = $json['description'];
    $obj['time'] = strtotime($json['date']);
    array_push($res['list'], $obj);
}

$res['title'] = 'HPC User Training 2021';

echo json_encode($res);

?>