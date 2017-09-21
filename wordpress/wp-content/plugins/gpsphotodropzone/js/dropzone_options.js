Dropzone.options.myform= {
    addRemoveLinks: true,
    autoProcessQueue: false,
    previewsContainer: "#dropzonePreview",
    autodiscover: false,
    parallelUploads: 4,
    maxFiles: 4,
    // The setting up of the dropzone
    init: function() {
        var myDropzone = this;

        // First change the button to actually tell Dropzone to process the queue.
        this.element.querySelector("button[type=submit]").addEventListener("click", function(e) {
          // Make sure that the form is not actually being sent.
          e.preventDefault();
          e.stopPropagation();
          myDropzone.processQueue();
        });

        // Listen to the sendingmultiple event. In this case, it is the sendingmultiple event instead
        // of the sending event because uploadMultiple is set to true.
        this.on("sendingmultiple", function() {
          // Gets triggered when the form is actually being sent.
          // Hide the success button or the complete form.
        });
        this.on("successmultiple", function(files, response) {
          // Gets triggered when the files have successfully been sent.
          // Redirect user or notify of success.
        });
        this.on("errormultiple", function(files, response) {
          // Gets triggered when there was an error sending the files.
          // Maybe show form again, and notify user of error
        });
    }
}

function b64EncodeUnicode(str) {
    // first we use encodeURIComponent to get percent-encoded UTF-8,
    // then we convert the percent encodings into raw bytes which
    // can be fed into btoa.
    return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g,
        function toSolidBytes(match, p1) {
            return String.fromCharCode('0x' + p1);
        }
    ));
};

var thispage = window.location.href;
//stateString = b64EncodeUnicode('{ "referer" : "http://gpsphoto.fritz.box/wordpress/index.php/incident-reporting-drop-zone/"}');
stateString = b64EncodeUnicode('{ "referer" : "' + thispage + '"}');

function login() {
    url = php_vars.site + "/logon?state=" + stateString;
    window.open(url,"_self")
}

