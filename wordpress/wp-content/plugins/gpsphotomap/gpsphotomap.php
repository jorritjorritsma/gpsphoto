<?php
/*
Plugin Name: gpsphotomap
Plugin URI: http://jorritsma.cc/gpsphoto
Description: Plugin to upload photos to the gpsphoto application
Version: 1.0
Author: Jorrit Jorritsma
Author URI: http://jorritsma.cc
*/

function gpsphotomap_html_form_code($username) {
    $form = '
    
    <!-- <script id="jsonfile" src="http://gpsphoto.fritz.box/get?f=pjson" type="text/javascript"></script> -->
        <div id="mapid" style="width: 800; height: 600px;"></div>

        <form class="form-horizontal" id="qform" action="#" name="qform">
<fieldset>

<!-- Form Name -->
<!-- <legend>Filter Events</legend> -->

<input name="baseurl" id="baseurl" value="http://gpsphoto.fritz.box/get" type="hidden">
<input name="timezone" id="timezone" value="" type="hidden">


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
  <label class="col-md-4 control-label" for="type">Event type</label>
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

<!-- Text input-->
<!--
<div class="form-group">
  <label class="col-md-4 control-label" for="user">Submitter</label>  
  <div class="col-md-4">
  <input id="user" name="user" placeholder="Submitters user name" class="form-control input-md" type="text">
  </div>
</div>
-->
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
    $current_user = wp_get_current_user();
    $username = $current_user->user_email;
    $form = gpsphotomap_html_form_code($username);
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
    wp_register_script('leaflet', 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.0.3/leaflet.js', __FILE__);
    wp_enqueue_script('leaflet');
    wp_register_script('pikaday', 'https://cdnjs.cloudflare.com/ajax/libs/pikaday/1.5.1/pikaday.js', __FILE__);
    wp_enqueue_script('pikaday');
    wp_register_script('jstz', 'https://cdnjs.cloudflare.com/ajax/libs/jstimezonedetect/1.0.6/jstz.min.js', __FILE__, '', '', true);
    wp_enqueue_script('jstz');
    wp_register_script('gpsphotomap', plugins_url('gpsphotomap.js', __FILE__), '', '',true);
    wp_enqueue_script('gpsphotomap');
}

add_action( 'wp_enqueue_scripts', 'gpsphotomap_adding_scripts' );
add_action( 'wp_enqueue_scripts', 'gpsphotomap_adding_styles' );
add_shortcode( 'gpsphotomap', 'gpsphotomap_shortcode' );

?>
