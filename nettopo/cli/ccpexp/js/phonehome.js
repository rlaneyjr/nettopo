var phonehome = (function() {
  //var caa_url = "https://demo.ciscoactiveadvisor.com/";
  var caa_url = "https://www.ciscoactiveadvisor.com/";
  //var caa_url = "https://op2-dev2-wprox1.cisco.com/";
  /***********************To do Internationalization***********************************/
  function loadAndDisplayLanguages() {

    //consoleLogMethodDetailsStart("phonehome.js", "loadAndDisplayLanguages()");

    $("#caaTab").text($.i18n.prop("caaTab"));
    $("#caaLinksTab").text($.i18n.prop("caaLinksTab"));
    $("#phonehome-legend").text($.i18n.prop("phonehome-legend"));
    $("#ccoUserLabel").html($.i18n.prop("ccoUserLabel") + ' <span class="ccpexpCSSReplaceClass820">*</span>:');
    $("#ccoPasswordLabel").html($.i18n.prop("ccoPasswordLabel") + ' <span class="ccpexpCSSReplaceClass821">*</span>:');
    $("#clearBtn").text($.i18n.prop("clearBtn"));
    $("#authenticateBtn").text($.i18n.prop("authenticateBtn"));
    $("#authenticatedBtn").text($.i18n.prop("authenticatedBtn"));
    $("#uploadBtn").text($.i18n.prop("uploadBtn"));
    $("#phonehomeLinkLegend").text($.i18n.prop("phonehomeLinkLegend"));
    $("#caaIntro").text($.i18n.prop("caaIntro"));
    $("#caaDevices").text($.i18n.prop("caaDevices"));
    $("#caaAlert").text($.i18n.prop("caaAlert"));
    $("#caaDescP1").text($.i18n.prop("caaDescP1"));
    $("#caaDescP2").text($.i18n.prop("caaDescP2"));

    $("#caaDescP3One").text($.i18n.prop("caaDescP3One"));
    $("#caaDescP3Two").text($.i18n.prop("caaDescP3Two"));
    $(".clickHere").text($.i18n.prop("clickHereStr"));

    $("#caaDescLi1").text($.i18n.prop("caaDescLi1"));
    $("#caaDescLi2").text($.i18n.prop("caaDescLi2"));
    $("#caaDescLi3").text($.i18n.prop("caaDescLi3"));
    $("#caaOffer").text($.i18n.prop("caaOffer"));
    $("#phoneHelpMessOne").text($.i18n.prop("phoneHelpMessOne"));
    $("#phoneHelpMessOneFullStop").text($.i18n.prop("fullStop"));
    $("#sampleConfigLink").text($.i18n.prop("clickHereStr"));

    $("#clickHere").text($.i18n.prop("clickHereStr"));
    $("#clickHereID").text($.i18n.prop("clickHereStr"));
    $("#clickHereFullStop").text($.i18n.prop("fullStop"));

    $("#phoneHelpMessTwo").text($.i18n.prop("phoneHelpMessTwo"));
    $("#phonehomedesc2").text($.i18n.prop("phonehomedesc2"));
    $("#phonehomePrivacy").text($.i18n.prop("phonehomePrivacy"));
    $("#ccoUser").attr("placeholder", $.i18n.prop("ccoUserLabel"));
    $("#ccoPassword").attr("placeholder", $.i18n.prop("ccoPasswordLabel"));
    $("#phonehomeErrorMessage").text($.i18n.prop("phonehomeErrorMessage"));

    //consoleLogMethodDetailsEnd("phonehome.js", "loadAndDisplayLanguages()");
  }

  // Upload of scanner xml
  function scannerUpload(csrf_artifact1) {
    //consoleLogMethodDetailsStart("phonehome.js", "scannerUpload()");
    var loggedin_url = caa_url + "asi/rs/SCANNER-UPLOAD?csrf_artifact=" + csrf_artifact1, xml, reg, hostNameValue = "",
        ipAddress = "", scannerMethod = "", sysDescription = "", version = "", hardwareSerialId = "", pid = "", vid = "",
        inventoryValues, uptime = "", macAddress = "", scannerXml, arr = [], healthMonitor = "";
    var showCommand = showCommandsOutput();
    reg = new RegExp("\\n", "");
    try {
      if (!shRunFormatLatest) {
        shRunFormatOutput = deviceCommunicator.getExecCmdOutput("show running-config | format");
        shRunFormatLatest = true;
      }
      xml = shRunFormatOutput;

      $(xml).find('hostname').each(function() {
        $(this).find('SystemNetworkName').each(function() {
          hostNameValue = $(this).text();
          return false;
        });
      });
      ipAddress = $(location).attr('host');

      scannerMethod = ($(location).attr('protocol')).slice(0, -1);

      if (clubbedCLIOutputAvailable && shVerFormatOdmOutput != null) {
        xml = shVerFormatOdmOutput;
      }
      else {
        xml = deviceCommunicator.getExecCmdOutput("show version | format " + deviceCommunicator.getInstallDir() + "/odm/overviewshVer.odm");
      }
      version = $(xml).find('Version').text();

      xml = deviceCommunicator.getExecCmdOutput("show arp | include " + ipAddress);
      var cols = xml.split(/ +/);
      if (cols[3] != null) {
        macAddress = cols[3].replace(/\./g, '').replace(/(.{2})/g, "$1:").slice(0, -1);
      }

      xml = deviceCommunicator.getExecCmdOutput("show hardware | include Processor board");
      if ((xml.indexOf("Processor board ID")) > -1) {
        var serialIdDetails = xml.split("Processor board ID ");
        if (serialIdDetails.length >= 2) {
          hardwareSerialId = serialIdDetails[1];
        }
      }

      xml = deviceCommunicator.getExecCmdOutput("show inventory | include " + hardwareSerialId);
      var rows = xml.split(reg), fields;
      for (var i = 0; i < rows.length; i++) {
        if (rows[i].indexOf("PID: ") > -1 && rows[i].indexOf("VID: ") > -1) {
          inventoryValues = rows[i].split(",");
          for (var j = 0; j < inventoryValues.length; j++) {
            if (inventoryValues[j].indexOf("PID: ") > -1) {
              fields = inventoryValues[j].split("PID: ");
              pid = fields[1];
            }
            else if (inventoryValues[j].indexOf("VID: ") > -1) {
              fields = inventoryValues[j].split("VID: ");
              vid = fields[1];
            }
          }
          break;
        }
      }

      rows = showCommand.version.split(reg);
      for (var i = 0; i < rows.length; i++) {
        if (rows[i].indexOf("uptime ") > -1) {
          fields = rows[i].split("uptime is ");
          uptime = fields[1];
          break;
        }
      }

      sysDescription = showCommand.version.split(/\n\s*\n/);
      healthMonitor = deviceCommunicator.getExecCmdOutput("show health-monitor");
    }
    catch (error) {
        isEmptyBlock = true;
    }

    arr = [{name: "userid", value: $('#ccoUser').val()},
      {name: "location", value: ""},
      {name: "protoVersion", value: version},
      {name: "hVersion", value: "1.0"},
      {name: "scannerMethod", value: scannerMethod},
      {name: "deviceType", value: pid},
      {name: "ipAddress", value: ipAddress},
      {name: "deviceClass", value: "router"},
      {name: "macAddress", value: macAddress},
      {name: "firmware", value: version},
      {name: "serialNo", value: hardwareSerialId},
      {name: "productID", value: pid},
      {name: "pidvid", value: vid},
      {name: "hostname", value: hostNameValue},
      {name: "sysDescription", value: sysDescription[0]},
      {name: "sysUptime", value: uptime},
      {name: "bootReason", value: ""},
      {name: "totalVisibleMemorySize", value: ""},
      {name: "imageName", value: ""},
      {name: "runningConfig", value: showCommand.runningConfig},
      {name: "snmp", value: showCommand.snmp},
      {name: "inventory", value: showCommand.inventory},
      {name: "version", value: showCommand.version},
      {name: "ipInterfaceBrief", value: showCommand.ipIntBrief},
      {name: "interfaceDesc", value: showCommand.interfaceDesc},
      {name: "macAddrTable", value: showCommand.macAddrTable},
      {name: "cdpNeighbors", value: showCommand.cdpNeighbor},
      {name: "healthMonitor", value: ""}];
    // Generating scanner xml
    scannerXml = deviceCommunicator.configureCommandsFromTemplate("ScannerPayloadTemplate.txt", arr, true);

    try {
      $.ajax(loggedin_url, {
        type: 'POST',
        contentType: 'application/xml',
        data: scannerXml,
        xhrFields: {withCredentials: true},
        crossDomain:true,
        success: function(response) {
          if ($(response).find('success').first().text() === "1") {
            //$('#uploadStatus').text("Configuration securely uploaded");
            $('#uploadStatus').text($.i18n.prop("configSecurityUploaded"));
          }
          else {
            $('#uploadStatus').text($.i18n.prop("unableUploadConfig"));
          }
        },
        error: function(xhr, textStatus, errorThrown) {
          $('#uploadStatus').text($.i18n.prop("unableUploadConfig"));
        }
      });
    }
    catch (error) {
      $('#uploadStatus').text($.i18n.prop("unableUploadConfig"));
    }
    //consoleLogMethodDetailsEnd("phonehome.js", "scannerUpload()");
  }

  function showCommandsOutput() {
    //consoleLogMethodDetailsStart("phonehome.js", "showCommandsOutput()");
    var versionOutput = "", runningConfig = "", snmp = "", inventory = "", ipIntBrief = "", interfaceDesc = "", macAddrTable = "",
        cdpNeighbor = "", regExpStr = "", regExp = "", replaceExp = "";
    try {
      versionOutput = deviceCommunicator.getExecCmdOutput("show version");
      runningConfig = deviceCommunicator.getExecCmdOutput("show running-config");
      snmp = deviceCommunicator.getExecCmdOutput("show snmp");
      inventory = deviceCommunicator.getExecCmdOutput("show inventory");
      ipIntBrief = deviceCommunicator.getExecCmdOutput("show ip interface brief");
      interfaceDesc = deviceCommunicator.getExecCmdOutput("show interfaces description");
      macAddrTable = deviceCommunicator.getExecCmdOutput("show mac-address-table");
      cdpNeighbor = deviceCommunicator.getExecCmdOutput("show cdp neighbors");

      // Sanitize running Config
      $.ajaxSetup({async: false});
      $.ajax({
        type: "GET",
        url: "../templates/masking_rule.xml",
        dataType: "xml",
        success: function(xml) {
          $(xml).find('MaskPattern').each(function() {
            try {
              regExpStr = $(this).find('Expression').text();
              replaceExp = $(this).find('Replacement').text();
              regExp = new RegExp(regExpStr, "gm");
              if (runningConfig.match(regExp)) {
                runningConfig = runningConfig.replace(regExp, "\n" + replaceExp);
              }
            }
            catch (e) {
                isEmptyBlock = true;
            }
          });
        }
      });
      $.ajaxSetup({async: true});
    }
    catch (error) {
        isEmptyBlock = true;
    }
    //consoleLogMethodDetailsEnd("phonehome.js", "showCommandsOutput()");
    return {
      runningConfig: runningConfig,
      version: versionOutput,
      snmp: snmp,
      inventory: inventory,
      ipIntBrief: ipIntBrief,
      interfaceDesc: interfaceDesc,
      macAddrTable: macAddrTable,
      cdpNeighbor: cdpNeighbor
    }
  }

  function setCookie(c_name, value) {
    //consoleLogMethodDetailsStart("phonehome.js", "setCookie()");
    var date = new Date();
    date.setTime(date.getTime() + (15 * 60 * 1000));
    document.cookie = c_name + "=" + escape(value) + "; expires=" + date.toGMTString();
    //consoleLogMethodDetailsEnd("phonehome.js", "setCookie()");
  }

  function getCookie(c_name) {
    //consoleLogMethodDetailsStart("phonehome.js", "getCookie()");
    if (document.cookie.length > 0) {
      c_start = document.cookie.indexOf(c_name + "=");
      if (c_start != -1) {
        c_start = c_start + c_name.length + 1;
        c_end = document.cookie.indexOf(";", c_start);
        if (c_end == -1){
          c_end = document.cookie.length;
        }
        //consoleLogMethodDetailsEnd("phonehome.js", "getCookie()");
        return unescape(document.cookie.substring(c_start, c_end));
      }
    }
    //consoleLogMethodDetailsEnd("phonehome.js", "getCookie()");
    return "";
  }

  function eraseCookie(name) {
    //consoleLogMethodDetailsStart("phonehome.js", "eraseCookie()");
    setCookie(name, "");
    //consoleLogMethodDetailsEnd("phonehome.js", "eraseCookie()");
  }

  function refresh() {
    //consoleLogMethodDetailsStart("phonehome.js", "refresh()");
    $('#phonehomeError').hide();
    //consoleLogMethodDetailsEnd("phonehome.js", "refresh()");
  }

  function enableAuthUploadBtn() {
    //consoleLogMethodDetailsStart("phonehome.js", "enableAuthUploadBtn()");
    $("#authenticateBtn").show();
    $("#authenticatedBtn").hide();
    $('#uploadBtn').hide();
    $('#uploadStatus').text("");
    //consoleLogMethodDetailsEnd("phonehome.js", "enableAuthUploadBtn()");
  }

  function disableAuthUploadBtn() {
    //consoleLogMethodDetailsStart("phonehome.js", "disableAuthUploadBtn()");
    $("#authenticateBtn").hide();
    $("#authenticatedBtn").show();
    $('#uploadStatus').text("");
    //consoleLogMethodDetailsEnd("phonehome.js", "disableAuthUploadBtn()");
  }

  function phoneHomeLoading() {
    //consoleLogMethodDetailsStart("phonehome.js", "phoneHomeLoading()");
    loadAndDisplayLanguages();
    // Warning message to be displayed for IE browsers
    if ($.browser.msie) {
      $('#tabs').append('<div id="browserInfoVer" class="browserInfo"></div>');
      $('#browserInfoVer').append('<p><div class="utmSprite information"></div><span id="browserInfoVerClose" class="browserInfoClose"></span>'+
                                  '<span id="browserInfoVerMessage" class="browserInfoMessage"><noscript id="scriptDisable">' +
                                  $.i18n.prop("ScriptMessage") + '</noscript></span></p>');
      $('#browserInfoVerMessage').html($.i18n.prop("caaBrowserVersion"));
      //$('#browserInfoVerClose').html("<a href='#' id='warningClose'><span class='closeButton' title='Close Info Window'></span></a>");
      $('#browserInfoVerClose').html("<a href='#' id='warningClose'><span class='closeButton' title='" + $.i18n.prop("closeInfoWindow") + "'></span></a>");
      $('#browserInfoVer').show();
      $('#warningClose').click(function() {
        $('#browserInfoVer').hide();
        return false;
      });
    }

    $('#phonehomeError').hide();
    $("#tabs").tabs();
    $('#hideAll').css('display', 'block');
    $('#phoneHomeForm').validate({
      errorElement: "div",
      errorPlacement: function(error, element) {
        error.insertAfter(element.parent());
      }
    });

    var csrf_artifact = getCookie("csrf_artifact"), userid = getCookie("userAuth"), login_url, logout_url;

    // In case user is already authenticated, then no need to authenticate again
    if (userid != null && userid !== "") {
      $('#ccoUser').val(userid);
      disableAuthUploadBtn();
      $('#uploadBtn').show();
    } else {
      enableAuthUploadBtn();
      $('#ccoUser').val("");
    }

    $("#authenticateBtn")
      .button()
      .click(function(e) {
        if ($('#phoneHomeForm').valid()) {
          blockPage("Applying");
          setTimeout(function() {
            login_url = caa_url + "asi/rs/authenticate";
            $.ajax(login_url, {
              type: 'POST',
              dataType: 'json',
              data: {
                username: $('#ccoUser').val(),
                password: $('#ccoPassword').val()
              },
              crossDomain: true,
              xhrFields: {withCredentials: true},
              success: function(response) {
                // Capture the current CSRF token for upcoming calls
                csrf_artifact = response.csrf_artifact;
                if (response.loggedIn) {
                  disableAuthUploadBtn();
                  setCookie("userAuth", $('#ccoUser').val());
                  setCookie("csrf_artifact", csrf_artifact);
                  scannerUpload(csrf_artifact);
                  refresh();
                } else if (response.loggedIn) {
                  //$('#phonehomeErrorMessage').html("Credentials entered are incorrect! Please try again.");
                  $('#phonehomeErrorMessage').html($.i18n.prop("credIncorrect"));
                  $('#phonehomeError').show();
                }
                $.unblockUI();
              },
              error: function() {
                //$('#phonehomeErrorMessage').html("Authentication has failed!"); //either due to CORS failure, bad URL or other problem
                $('#phonehomeErrorMessage').html($.i18n.prop("phonehomeErrorMessage"));
                $('#phonehomeError').show();
                $.unblockUI();
              }
            });
            return false;
          }, 1000);
          e.preventDefault();
        }
      });

    $("#uploadBtn")
      .button()
      .click(function(e) {
        blockPage("Applying");
        setTimeout(function() {
          try {
            var csrfToken = getCookie("csrf_artifact");
            if (csrfToken != null && csrfToken !== "") {
              scannerUpload(csrfToken);
            }
            else {
              //$('#phonehomeErrorMessage').html("Session has timed out! Please provide your credentials again.");
              $('#phonehomeErrorMessage').html($.i18n.prop("sessionTimeout"));
              $('#phonehomeError').show();
              enableAuthUploadBtn();
            }
          }
          catch (e) {
            $('#uploadStatus').text($.i18n.prop("unableUploadConfig"));
          }
          $.unblockUI();
          return false;
        }, 1000);
        e.preventDefault();
      });

    $("#clearBtn")
      .button()
      .click(function(e) {
        refresh();
        //Clear STD cookie on server side
        csrf_artifact = getCookie("csrf_artifact");
        if (csrf_artifact != null && csrf_artifact !== "") {
          logout_url = caa_url + "asi/rs/logout?csrf_artifact=" + csrf_artifact;
          $.ajax(logout_url, {
            type: 'GET',
            xhrFields: {withCredentials: true}
          });
        }
        eraseCookie("userAuth");
        eraseCookie("csrf_artifact");
        userid = "";
        csrf_artifact = "";
        $('#ccoUser').val("");
        $('#ccoPassword').val("");
        enableAuthUploadBtn();
        return false;
      });

    $("#authenticatedBtn")
      .button()
      .click(function(e) {
        return false;
      });
    // Display sample data based on router details
    $('a#sampleConfigLink').click(function() {
      var showCommand = showCommandsOutput(), arr = [], sampleConfig = "";
      arr = [{name: "runningConfig", value: showCommand.runningConfig},
        {name: "version", value: showCommand.version},
        {name: "snmp", value: showCommand.snmp},
        {name: "inventory", value: showCommand.inventory},
        {name: "ipIntBrief", value: showCommand.ipIntBrief},
        {name: "interfaceDesc", value: showCommand.interfaceDesc},
        {name: "macAddrTable", value: showCommand.macAddrTable},
        {name: "cdpNeighbor", value: showCommand.cdpNeighbor}];
      sampleConfig = deviceCommunicator.configureCommandsFromTemplate("sampleSwitchConfiguration.txt", arr, true);
      $("#sampleConfig").val(sampleConfig);
      $('#sampleConfigDialog').dialog('open');
    });

    $("#sampleConfigDialog").dialog({
      autoOpen: false,
      modal: true,
      height: 430,
      width: 650,
      buttons: {
        Close: function() {
          $("#sampleConfig").val("");
          $(this).dialog("close");
        }
      },
      close: function() {
      }
    });

    $('#hideAll').css('display', 'none');
    //consoleLogMethodDetailsEnd("phonehome.js", "phoneHomeLoading()");
  }
  return {
    phoneHomeLoading: phoneHomeLoading
  };
}());
