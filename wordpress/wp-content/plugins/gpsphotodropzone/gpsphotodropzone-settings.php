<?php
// create custom plugin settings menu
add_action('admin_menu', 'gpsphotodropzone_create_menu');

function gpsphotodropzone_create_menu() {

    //create new top-level menu
    //add_menu_page('GPSPhotoMap Plugin Settings', 'GPSPhotomap Settings', 'administrator', __FILE__, 'gpsphotodropzone_settings_page' , plugins_url('/images/icon.png', __FILE__) );
    add_options_page('GPSPhotoDropZone Settings', 'GPSPhotoDropZone', 'administrator', __FILE__, 'gpsphotodropzone_settings_page' );

    //call register settings function
    add_action( 'admin_init', 'register_gpsphotodropzone_settings' );
    //add_action( 'admin_menu', 'register_gpsphotodropzone_settings' );
}


function register_gpsphotodropzone_settings() {
    //register our settings
    register_setting( 'gpsphotodropzone_settings_group', 'gpsphoto_server' );
    register_setting( 'gpsphotodropzone_settings_group', 'gpsphoto_organization' );
}

function gpsphotodropzone_settings_page() {
?>
<div class="wrap">
<h1>GPSPhotomap</h1>

<form method="post" action="options.php">
    <?php settings_fields( 'gpsphotodropzone_settings_group' ); ?>
    <?php do_settings_sections( 'gpsphotodropzone_settings_group' ); ?>
    <table class="form-table">
        <tr valign="top">
        <th scope="row">GPSPhoto back-end server URL</th>
        <td><input type="text" name="gpsphoto_server" value="<?php echo esc_attr( get_option('gpsphoto_server') ); ?>" /></td>
        </tr>
         
        <tr valign="top">
        <th scope="row">Organization</th>
        <td><input type="text" name="gpsphoto_organization" value="<?php echo esc_attr( get_option('gpsphoto_organization') ); ?>" /></td>
        </tr>
        
    </table>
    
    <?php submit_button(); ?>

</form>
</div>
<?php } ?>
