<?php
// If this file is called directly, abort.
if (! defined('WPINC')) {
    die;
}

//include 'gpsphoto-settings.php';

function gpsphotodropzone_html_form_code($server, $org, $types, $askformail, $event, $epoch) {
    $form = '
          <div class="control-group">
             <a href="#" id="login" onclick=login()><img src="' . $server . '/gpsphoto/secure/logged_in.png?' . $epoch . '" width="150" onerror="this.onerror=null;this.src=' . "'" . $server . '/gpsphoto/logged_out.png' . "'" . ';" /></a><p/>
          </div>

    <div id="mydropzone">
      <form id="myform" method="post" enctype="multipart/form-data" action="' . $server . '/upload" class="dropzone needsclick">
      <div class="form-horizontal">
        <fieldset>
       <input type="hidden" name="org" value="' . $org . '">
       <input type="hidden" name="event" value="' . $event . '">
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
          <!--
          <div class="form-group">
            <label class="col-md-3 control-label" for="event">Event</label>  
            <div class="col-md-9">
              <input id="title" name="event" placeholder="Event name" class="form-control input-md" type="text">
            </div>
          </div>
          -->

          <!-- Select Basic -->
          <div class="form-group">
            <label class="col-md-3 control-label" for="type">Type</label>
            <div class="col-md-9">
              <select id="type" name="type" class="form-control">';

    foreach(explode(',', $types) as $type) {
        $form .= '                <option value="' . $type . '">' . $type . '</option>';
    }

    $form .= '
              </select>
            </div>
          </div>
          <!-- Textarea -->
          <div class="form-group">
            <label class="col-md-3 control-label" for="description">Description</label>
            <div class="col-md-9">                     
              <textarea class="form-control" id="description" name="description" placeholder="Provide a description of what can be seen on the photo(s)"></textarea>
            </div>
          </div>';
    
    // If configured in amdin menu, provide field to leave email address
    if ( $askformail == 1 ) {
      $form .= '
          <!-- Textarea -->
          <div class="form-group">
            <label class="col-md-3 control-label" for="description">Your email address</label>
            <div class="col-md-9">
              <input id="emailaddr" name="emailaddr" placeholder="Let us know how we can reach you." class="form-control input-md" type="text">
            </div>
          </div>';
    }

          $form .= '
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
    $options = get_option( 'gpsphoto_settings' );
    $epoch = time();
    $current_user = wp_get_current_user();
    $form = gpsphotodropzone_html_form_code($options['server'], $options['org'], $options['types'], $options['askformail'], $options['event'], $epoch);

    echo $form;
    return ob_get_clean();
}

function gpsphotodropzone_adding_styles() {
    wp_register_style('bootstrap', 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css', __FILE__);
    wp_enqueue_style('bootstrap');
    wp_register_style('dropzonecss', 'https://cdnjs.cloudflare.com/ajax/libs/dropzone/4.3.0/min/dropzone.min.css', __FILE__);
    wp_enqueue_style('dropzonecss');

}
	
function gpsphotodropzone_adding_scripts() {
    $options = get_option( 'gpsphoto_settings' );
    wp_register_script('dropzoneoptions', plugins_url('js/dropzone_options.js', __FILE__), '', '', true);
    wp_enqueue_script('dropzoneoptions');
    wp_register_script('dropzone', 'https://cdnjs.cloudflare.com/ajax/libs/dropzone/4.3.0/min/dropzone.min.js', __FILE__);
    wp_enqueue_script('dropzone');
    $dataToBePassed = array(
    'server'            => $options['server']);
    wp_localize_script( 'dropzoneoptions', 'php_vars', $dataToBePassed );
}

add_action( 'wp_enqueue_scripts', 'gpsphotodropzone_adding_scripts' );
add_action( 'wp_enqueue_scripts', 'gpsphotodropzone_adding_styles' );
add_shortcode( 'gpsphotodropzone', 'gpsphotodropzone_shortcode' );

?>
