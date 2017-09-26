<?php
// create custom plugin settings menu
add_action('admin_menu', 'gpsphotomap_create_menu');

function gpsphotomap_create_menu() {

    //create new top-level menu
    //add_menu_page('GPSPhotoMap Plugin Settings', 'GPSPhotomap Settings', 'administrator', __FILE__, 'gpsphotomap_settings_page' , plugins_url('/images/icon.png', __FILE__) );
    add_options_page('GPSPhotoMap Settings', 'GPSPhotoMap', 'administrator', __FILE__, 'gpsphotomap_settings_page' );

    //call register settings function
    add_action( 'admin_init', 'register_gpsphotomap_settings' );
    //add_action( 'admin_menu', 'register_gpsphotomap_settings' );
}


function register_gpsphotomap_settings() {
    //register our settings
    register_setting( 'gpsphotomap_settings_group', 'gpsphoto_server' );
    register_setting( 'gpsphotomap_settings_group', 'gpsphoto_organization' );
    register_setting( 'gpsphotomap_settings_group', 'gpsphoto_longitude' );
    register_setting( 'gpsphotomap_settings_group', 'gpsphoto_latitude' );
    register_setting( 'gpsphotomap_settings_group', 'gpsphoto_zoomlevel' );
}

function gpsphotomap_settings_page() {
?>
<div class="wrap">
<h1>GPSPhotomap</h1>

<form method="post" action="options.php">
    <?php settings_fields( 'gpsphotomap_settings_group' ); ?>
    <?php do_settings_sections( 'gpsphotomap_settings_group' ); ?>
    <table class="form-table">
        <tr valign="top">
        <th scope="row">GPSPhoto server URL</th>
        <td><input type="text" name="gpsphoto_server" value="<?php echo esc_attr( get_option('gpsphoto_server') ); ?>" /></td>
        </tr>
         
        <tr valign="top">
        <th scope="row">Organization</th>
        <td><input type="text" name="gpsphoto_organization" value="<?php echo esc_attr( get_option('gpsphoto_organization') ); ?>" /></td>
        </tr>
        
        <tr valign="top">
        <td colspan="2">Set the center of the map. You can get the coordinates from <a href="https://www.latlong.net/" target="_blank">https://www.latlong.net/</a></td>
        </tr>

        <tr valign="top">
        <th scope="row">Longitude</th>
        <td><input type="text" name="gpsphoto_longitude" value="<?php echo esc_attr( get_option('gpsphoto_longitude') ); ?>" /></td>
        </tr>
        
        <tr valign="top">
        <th scope="row">Latitude</th>
        <td><input type="text" name="gpsphoto_latitude" value="<?php echo esc_attr( get_option('gpsphoto_latitude') ); ?>" /></td>
        </tr>
        
        <tr valign="top">
        <td colspan="2">Set the zoom level to 0 to 19, where 0 is the whole world.</td>
        </tr>

        <tr valign="top">
        <th scope="row">Zoom level</th>
        <td><input type="text" name="gpsphoto_zoomlevel" value="<?php echo esc_attr( get_option('gpsphoto_zoomlevel') ); ?>" /></td>
        </tr>
        
    </table>
    
    <?php submit_button(); ?>

</form>
</div>
<?php } ?>
