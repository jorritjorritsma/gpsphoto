<?php
// If this file is called directly, abort.
if ( ! defined( 'WPINC' ) ) {
    die;
}

//include 'gpsphoto-settings.php';

function gpsphotomap_html_form_code($server, $org, $types) {
    $form = '
        <div id="mapid" style="width: 800; height: 600px;"></div>
        <form class="form-horizontal" id="qform" action="#" name="qform">
<fieldset>

<input name="timezone" id="timezone" value="" type="hidden">
<input name="org" id="org" value="' . $org . '" type="hidden">

<!-- Text input-->
<div class="form-group">
  <label class="col-md-4 control-label" for="begindate">From date</label>  
  <div class="col-md-3">
  <input id="begindate" name="begindate" placeholder="From date" class="form-control input-md" type="text">
  </div>
</div>

<!-- Text input-->
<div class="form-group">
  <label class="col-md-4 control-label" for="enddate">To Date</label>  
  <div class="col-md-3">
  <input id="enddate" name="enddate" placeholder="Filter end date" class="form-control input-md" type="text">
  </div>
</div>

<!-- Select Basic -->
<div class="form-group">
  <label class="col-md-4 control-label" for="type">Incident type</label>
  <div class="col-md-4">
    <select id="Type" name="type" class="form-control">
        <option selected="selected" value="">All</option>';

    foreach(explode(',', $types) as $type) {
        $form .= '                <option value="' . $type . '">' . $type . '</option>';
    }

    $form .= '
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
    $options = get_option('gpsphoto_settings');
    $form = gpsphotomap_html_form_code($options['server'], $options['org'], $options['types']);
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
    $options = get_option('gpsphoto_settings');
    wp_register_script('leaflet', 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.0.3/leaflet.js', __FILE__);
    wp_enqueue_script('leaflet');
    wp_register_script('pikaday', 'https://cdnjs.cloudflare.com/ajax/libs/pikaday/1.5.1/pikaday.js', __FILE__);
    wp_enqueue_script('pikaday');
    wp_register_script('jstz', 'https://cdnjs.cloudflare.com/ajax/libs/jstimezonedetect/1.0.6/jstz.min.js', __FILE__, '', '', true);
    wp_enqueue_script('jstz');
    wp_register_script('mapoptions', plugins_url('js/map_options.js', __FILE__), '', '',true);
    wp_enqueue_script('mapoptions');
    // arguments we want to use in javascript:
    $dataToBePassed = array(
    'server'          => $options['server'],
    'org'             => $options['org'],
    'types'           => $options['types'],
    'longitude'       => $options['longitude'],
    'latitude'        => $options['latitude'],
    'zoomlevel'       => $options['zoomlevel']);
    wp_localize_script( 'mapoptions', 'php_vars', $dataToBePassed );

}

add_action( 'wp_enqueue_scripts', 'gpsphotomap_adding_scripts' );
add_action( 'wp_enqueue_scripts', 'gpsphotomap_adding_styles' );
add_shortcode( 'gpsphotomap', 'gpsphotomap_shortcode' );

?>
