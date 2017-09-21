<?php
/*
Plugin Name: gpsphotodropzone
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

include 'gpsphotodropzone-settings.php';

$site = get_option('gpsphoto_server');
$org = get_option('gpsphoto_organization');
$epoch = time();

function gpsphotodropzone_html_form_code($site, $org, $username, $epoch) {
    $form = '
          <div class="control-group">
             <a href="#" id="login" onclick=login()><img src="' . $site . '/secure/logged_in.png?' . $epoch . '" width="150" onerror="this.onerror=null;this.src=' . "'" . $site . '/logged_out.png' . "'" . ';" /></a><p/>
          </div>

    <div id="mydropzone">
      <form id="myform" action="' . $site . '/upload" class="dropzone needsclick">
      <div class="form-horizontal">
        <fieldset>
       <input type="hidden" name="emailaddr" value="' . $username . '">
       <input type="hidden" name="org" value="' . $org . '">
          <!-- Form Name -->
          <!-- <legend>Report Incident by Photo Location</legend> -->
          <!-- Text input-->
          <div class="form-group">
            <label class="col-md-3 control-label" for="title">Title</label>  
            <div class="col-md-9">
              <input id="title" name="title" placeholder="Title of photo(s)" class="form-control input-md" type="text">
            </div>
          </div>
          <!-- Text input-->
          <div class="form-group">
            <label class="col-md-3 control-label" for="event">Event</label>  
            <div class="col-md-9">
              <input id="title" name="event" placeholder="Event name" class="form-control input-md" type="text">
            </div>
          </div>
          <!-- Select Basic -->
          <div class="form-group">
            <label class="col-md-3 control-label" for="type">Incident Type</label>
            <div class="col-md-9">
              <select id="type" name="type" class="form-control">
                <option value="nice">Nice</option>
                <option value="notable">Notable</option>
                <option value="threat">Threat</option>
                <option value="harassment">Harassment</option>
                <option value="aggression">Aggression</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          <!-- Textarea -->
          <div class="form-group">
            <label class="col-md-3 control-label" for="description">Description</label>
            <div class="col-md-9">                     
              <textarea class="form-control" id="description" name="description" placeholder="Provide a description of the event visible on the photo(s)"></textarea>
            </div>
          </div>
          <!-- Button -->
          <div class="form-group">
            <label class="col-md-3 control-label" for="submit"></label>
            <div class="col-md-4">
              <button id="submit" type="submit" class="btn btn-primary">Submit</button>
            </div>
          </div>
          <p>
          </p>
        </div>
      </fieldset>
      <div id="dropzonePreview" class="dz-message needsclick">
        <h1><b>Drop files here or click to upload.</b></h><br />
      </div>
      </form>
    </div>
    ';
    return($form);
}

function gpsphotodropzone_shortcode() {
    ob_start();
    global $site;
    global $org;
    global $epoch;
	$current_user = wp_get_current_user();
	$username = $current_user->user_email;
	$form = gpsphotodropzone_html_form_code($site, $org, $username, $epoch);

	echo $form;
	return ob_get_clean();
}

function gpsphotodropzone_adding_styles() {
	wp_register_style('bootstrap', 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css
/bootstrap.min.css', __FILE__);
	wp_enqueue_style('bootstrap');
        wp_register_style('dropzonecss', 'https://cdnjs.cloudflare.com/ajax/libs/dropzone/4.3.0/min/dropzone.min.css', __FILE__);
        wp_enqueue_style('dropzonecss');

}
	
function gpsphotodropzone_adding_scripts() {
    global $site;
	wp_register_script('dropzoneoptions', plugins_url('js/dropzone_options.js', __FILE__), '', '', true);
	wp_enqueue_script('dropzoneoptions');
        wp_register_script('dropzone', 'https://cdnjs.cloudflare.com/ajax/libs/dropzone/4.3.0/min/dropzone.min.js', __FILE__);
	wp_enqueue_script('dropzone');
    $dataToBePassed = array(
    'site'            => $site);
    wp_localize_script( 'dropzone', 'php_vars', $dataToBePassed );
}

add_action( 'wp_enqueue_scripts', 'gpsphotodropzone_adding_scripts' );
add_action( 'wp_enqueue_scripts', 'gpsphotodropzone_adding_styles' );
add_shortcode( 'gpsphotodropzone', 'gpsphotodropzone_shortcode' );

?>
