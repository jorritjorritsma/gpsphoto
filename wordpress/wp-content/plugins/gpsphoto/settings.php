<?php
// If this file is called directly, abort.
if ( ! defined( 'WPINC' ) ) {
    die;
}

add_action( 'admin_menu', 'gpsphoto_add_admin_menu' );
add_action( 'admin_init', 'gpsphoto_settings_init' );

function gpsphoto_add_admin_menu(  ) { 
    add_options_page( 'GPSPhoto', 'GPSPhoto', 'manage_options', 'gpsphoto', 'gpsphoto_options_page' );
}

function gpsphoto_settings_init(  ) { 
    register_setting( 'pluginPage', 'gpsphoto_settings' );

    add_settings_section(
        'gpsphoto_pluginPage_general_section', 
        __( 'General Settings', 'wordpress' ), 
        'gpsphoto_settings_general_section_callback', 
        'pluginPage'
    );

    add_settings_field( 
        'server', 
        __( 'GPSPhoto server', 'wordpress' ), 
        'gpsphoto_server_render', 
        'pluginPage', 
        'gpsphoto_pluginPage_general_section' 
    );

    add_settings_field( 
        'org', 
        __( 'Organization', 'wordpress' ), 
        'gpsphoto_org_render', 
        'pluginPage', 
        'gpsphoto_pluginPage_general_section' 
    );

    add_settings_field( 
        'types', 
        __( 'Types (comma separated)', 'wordpress' ), 
        'gpsphoto_types_render', 
        'pluginPage', 
        'gpsphoto_pluginPage_general_section' 
    );

    add_settings_section(
        'gpsphoto_pluginPage_dropzone_section', 
        __( 'DropZone Settings', 'wordpress' ), 
        'gpsphoto_settings_dropzone_section_callback', 
        'pluginPage'
    );

    add_settings_field( 
        'event', 
        __( 'Event', 'wordpress' ), 
        'gpsphoto_event_render', 
        'pluginPage', 
        'gpsphoto_pluginPage_dropzone_section' 
    );

    add_settings_field( 
        'askformail', 
        __( "Provide email field?", 'wordpress' ), 
        'gpsphoto_askformail_render', 
        'pluginPage', 
        'gpsphoto_pluginPage_dropzone_section' 
    );

    add_settings_section(
        'gpsphoto_pluginPage_map_section', 
        __( 'Map Settings', 'wordpress' ), 
        'gpsphoto_settings_map_section_callback', 
        'pluginPage'
    );

    add_settings_field( 
        'longitude', 
        __( "Longitude", 'wordpress' ), 
        'gpsphoto_longitude_render', 
        'pluginPage', 
        'gpsphoto_pluginPage_map_section' 
    );

    add_settings_field( 
        'latitude', 
        __( "Latitude", 'wordpress' ), 
        'gpsphoto_latitude_render', 
        'pluginPage', 
        'gpsphoto_pluginPage_map_section' 
    );

    add_settings_field( 
        'zoomlevel', 
        __( "Initial zoom level", 'wordpress' ), 
        'gpsphoto_zoomlevel_render', 
        'pluginPage', 
        'gpsphoto_pluginPage_map_section' 
    );
}

function gpsphoto_server_render(  ) { 
    $options = get_option( 'gpsphoto_settings' );
    ?>
    <input type='text' name='gpsphoto_settings[server]' value='<?php echo $options['server']; ?>'>
    <?php
}

function gpsphoto_org_render(  ) { 
    $options = get_option( 'gpsphoto_settings' );
    ?>
    <input type='text' name='gpsphoto_settings[org]' value='<?php echo $options['org']; ?>'>
    <?php
}

function gpsphoto_types_render(  ) { 
    $options = get_option( 'gpsphoto_settings' );
    ?>
    <input type='text' name='gpsphoto_settings[types]' value='<?php echo esc_attr($options['types']); ?>'>
    <?php
}

function gpsphoto_event_render(  ) { 
    $options = get_option( 'gpsphoto_settings' );
    ?>
    <input type='text' name='gpsphoto_settings[event]' value='<?php echo $options['event']; ?>'>
    <?php
}

function gpsphoto_askformail_render(  ) { 
    $options = get_option( 'gpsphoto_settings' );
    ?>
    <input type='checkbox' name='gpsphoto_settings[askformail]' <?php checked( $options['askformail'], 1 ); ?> value='1'>
    <?php
}

function gpsphoto_longitude_render(  ) { 
    $options = get_option( 'gpsphoto_settings' );
    ?>
    <input type='text' name='gpsphoto_settings[longitude]' value='<?php echo $options['longitude']; ?>'>
    <?php
}

function gpsphoto_latitude_render(  ) { 
    $options = get_option( 'gpsphoto_settings' );
    ?>
    <input type='text' name='gpsphoto_settings[latitude]' value='<?php echo $options['latitude']; ?>'>
    <?php
}

function gpsphoto_zoomlevel_render(  ) { 
    $options = get_option( 'gpsphoto_settings' );
    ?>
    <input type='text' name='gpsphoto_settings[zoomlevel]' value='<?php echo $options['zoomlevel']; ?>'>
    <?php
}


function gpsphoto_settings_general_section_callback(  ) { 
    echo __( "The below settings are both used by the GPSPhoto Map and GPSPhoto DropZone plugins.<br>You must specify the back-end server such as https://gpsphotomap.com.<br>If you have a subscription on gpsphotomap.com (if that is where your gpsphoto back-end is hosted), specify your organization string, if you don't have one your entries will be submitted to the default database.<br>To classify the incident reports provide a list of classes you want to report against.", 'wordpress' );
}

function gpsphoto_settings_dropzone_section_callback(  ) { 
    echo __( "The settings in this section only apply to the dropzone plugin<br>The 'Event' field can be used to provide an event name the incidents are logged for, this will allow filtering on that event in the map.<br>Tick the 'Provide email field' if you want to give the reporter the option to leave an email address other than the one they logged in with at gpsphotomap.com.", 'wordpress' );
}

function gpsphoto_settings_map_section_callback(  ) { 
    echo __( "Here you can specify the default view of the map by specifying the center point in latitude and longitude (visiting https://www.latlong.net might help) and zoom level of the map (0 - 19 where 0 is the whole world). .", 'wordpress' );
}

function gpsphoto_options_page(  ) { 
    ?>
    <form action='options.php' method='post'>
        <h2>GPSPhoto</h2>

        <?php
        settings_fields( 'pluginPage' );
        do_settings_sections( 'pluginPage' );
        submit_button();
        ?>

    </form>
    <?php
}
?>
