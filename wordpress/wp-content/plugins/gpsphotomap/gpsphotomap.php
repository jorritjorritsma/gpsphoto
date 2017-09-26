<?php
/*
Plugin Name: gpsphotomap
Plugin URI: https://jorritsma.cc/gpsphoto
Description: Plugin to upload photos to the gpsphoto application
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

include 'gpsphotomap-settings.php';

$site = get_option('gpsphoto_server');
$org = get_option('gpsphoto_organization');
$longitude = get_option('gpsphoto_longitude');
$latitude = get_option('gpsphoto_latitude');
$zoomlevel = get_option('gpsphoto_zoomlevel');

function gpsphotomap_html_form_code($site, $org, $username) {
    $form = '
        <div id="mapid" style="width: 800; height: 600px;"></div>
        <form class="form-horizontal" id="qform" action="#" name="qform">
<fieldset>

<input name="timezone" id="timezone" value="" type="hidden">
<input name="org" id="org" value="' . $org . '" type="hidden">

<!-- Text input-->
<div class="form-group">
  <label class="col-md-4 control-label" for="enddate">End Date</label>  
  <div class="col-md-3">
  <input id="enddate" name="enddate" placeholder="Filter end date" class="form-control input-md" type="text">
  </div>
</div>

<!-- Select Basic -->
<div class="form-group">
  <label class="col-md-4 control-label" for="numberofdays">Days before</label>
  <div class="col-md-4">
    <select id="numberofdays" name="numberofdays" class="form-control">
      <option selected="selected"value="">All</option>
      <option value="1">1 day</option>
      <option value="2">2 days</option>
      <option value="3">3 days</option>
      <option value="4">4 days</option>
      <option value="5">5 days</option>
      <option value="6">6 days</option>
      <option value="7">1 week</option>
      <option value="14">2 weeks</option>
      <option value="21">3 weeks</option>
      <option value="28">4 weeks</option>
    </select>
  </div>
</div>

<!-- Select Basic -->
<div class="form-group">
  <label class="col-md-4 control-label" for="type">Incident type</label>
  <div class="col-md-4">
    <select id="Type" name="type" class="form-control">
        <option selected="selected" value="">All</option>
        <option value="nice">Nice memories</option>
        <option value="notable">Notable</option>
        <option value="threatening">Threatening</option>
        <option value="harassmnet">Harassment</option>
        <option value="aggression">Aggression</option>
        <option value="other">Other evidence</option>
    </select>
  </div>
</div>

<!-- Select Basic -->
<div class="form-group">
  <label class="col-md-4 control-label" for="event">Event</label>
  <div class="col-md-4">
    <input type="text" id="Event" name="event" class="form-control">
  </div>
</div>

<!-- Text input-->
<div class="form-group">
  <label class="col-md-4 control-label" for="user">Submitter</label>  
  <div class="col-md-4">
  <input id="user" name="user" placeholder="Submitters user name" class="form-control input-md" type="text">
  </div>
</div>

<!-- Select Basic -->
<div class="form-group">
  <label class="col-md-4 control-label" for="verified">Verified submissions</label>
  <div class="col-md-4">
    <select id="Verified" name="verified" class="form-control">
        <option selected="selected" value="">All</option>
        <option value="true">Verified</option>
        <option value="false">Not verified</option>
    </select>
  </div>
</div>

<!-- Button -->
<div class="form-group">
  <label class="col-md-4 control-label" for="submitbutton"></label>
  <div class="col-md-4">
    <input name="submit" value="Submit" onclick="getFormData();" type="button" class="btn btn-primary">
    <!-- <button id="submitbutton" name="submitbutton" onclick="getFormData(); class="btn btn-primary">Filter</button> -->
  </div>
</div>

</fieldset>
</form>';
    return($form);
}

function gpsphotomap_shortcode() {
    ob_start();
    global $site;
    global $org;
    $current_user = wp_get_current_user();
    $username = $current_user->user_email;
    $form = gpsphotomap_html_form_code($site, $org, $username);
    echo $form;
    return ob_get_clean();
}

function gpsphotomap_adding_styles() {
    wp_register_style('leafletcss', 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.0.3/leaflet.css', __FILE__);
    wp_enqueue_style('leafletcss');
    wp_register_style('pikadaycss', 'https://cdnjs.cloudflare.com/ajax/libs/pikaday/1.5.1/css/pikaday.min.css', __FILE__);
    wp_enqueue_style('pikadaycss');
    wp_register_style('bootstrap', 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css', __FILE__);
    wp_enqueue_style('bootstrap');    
}
    
function gpsphotomap_adding_scripts() {
    global $site;
    global $org;
    global $longitude;
    global $latitude;
    global $zoomlevel;
    wp_register_script('leaflet', 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.0.3/leaflet.js', __FILE__);
    wp_enqueue_script('leaflet');
    wp_register_script('pikaday', 'https://cdnjs.cloudflare.com/ajax/libs/pikaday/1.5.1/pikaday.js', __FILE__);
    wp_enqueue_script('pikaday');
    wp_register_script('jstz', 'https://cdnjs.cloudflare.com/ajax/libs/jstimezonedetect/1.0.6/jstz.min.js', __FILE__, '', '', true);
    wp_enqueue_script('jstz');
    wp_register_script('gpsphotomap', plugins_url('js/gpsphotomap.js', __FILE__), '', '',true);
    wp_enqueue_script('gpsphotomap');
    $dataToBePassed = array(
    'site'            => $site,
    'org'             => $org,
    'longitude'       => $longitude,
    'latitude'        => $latitude,
    'zoomlevel'       => $zoomlevel);
    wp_localize_script( 'gpsphotomap', 'php_vars', $dataToBePassed );

}

add_action( 'wp_enqueue_scripts', 'gpsphotomap_adding_scripts' );
add_action( 'wp_enqueue_scripts', 'gpsphotomap_adding_styles' );
add_shortcode( 'gpsphotomap', 'gpsphotomap_shortcode' );

?>
