<?php
/*
Plugin Name: gpsphoto
Plugin URI: https://jorritsma.cc/gpsphoto
Description: Plugin to upload photos to the gpsphoto application and display uploaded photos on a map
Version: 1.1
Author: Jorrit Jorritsma
Author URI: https://jorritsma.cc
License: GPL-3.0
License URI: https://www.gnu.org/licenses/gpl-3.0.txt
*/
// If this file is called directly, abort.
if ( ! defined( 'WPINC' ) ) {
    die;
}

include dirname(__FILE__) . '/settings.php';
include dirname(__FILE__) . '/map.php';
include dirname(__FILE__) . '/dropzone.php';
?>
