// JavaScript Document

function getUrlVariables() {
  //consoleLogMethodDetailsStart("frames.js", "getUrlVariables()");
  var vars = [], hash, hashes, i;
  hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
  for (i = 0; i < hashes.length; i = i + 1) {
    hash = hashes[i].split('=');
    vars.push(hash[0]);
    vars[hash[0]] = hash[1];
  }
  //consoleLogMethodDetailsEnd("frames.js", "getUrlVariables()");
  return vars;
}
//To get languageName
//function languageName() {
//    var tempLang,Lang="";
//    tempLang=$.i18n.browserLang();
//    Lang="e";
//    if ((tempLang==="en-US")||(tempLang==="en")) {
//                Lang="e";
//    }
//    else if ((tempLang==="fr-FR")||(tempLang==="fr")) {
//                Lang="fr";
//    }
//   return Lang;
//}

/*function openGoogleAnalyticsDialog() {
  //consoleLogMethodDetailsStart("frames.js", "openGoogleAnalyticsDialog()");
  if (checkCookie() == 'true') {
    getGATrackCode();
  }

  //consoleLogMethodDetailsEnd("frames.js", "openGoogleAnalyticsDialog()");

}*/

function enableDisableDashboard() {
  //consoleLogMethodDetailsStart("frames.js", "enableDisableDashboard()");
  if (!licenseCheck) {
    if (iosk9check == "SecurityEnable") {
      //$('#bottomnav-11').show();
      $("#securityDashboard").show();
    } else {
      $("#securityDashboard").hide();
    }
  }
  else {
    $("#securityDashboard").show();
  }
  //consoleLogMethodDetailsEnd("frames.js", "enableDisableDashboard()");
}

function copyClipboard(){
  var copyDiv = document.getElementById('temp');
  copyDiv.focus();
  document.execCommand('SelectAll');
  document.execCommand("Copy", false, null);
}


/*function checkCookie() {
  //consoleLogMethodDetailsStart("frames.js", "checkCookie()");
  if (GetCookie(name) == null || GetCookie(name) == "undefined") {
    if (isCookiesEnabled()) {
      $("#googleAnalyticsPopUp").dialog("open");
    }
    return 'false';
  }
  else {
    return GetCookie(name);
  }
  //consoleLogMethodDetailsEnd("frames.js", "checkCookie()");

}*/

/*function checkSecurityLicense() {
 var found=false;
 resp = deviceCommunicator.getExecCmdOutput("show license feature");
 licenseSplit=resp.split("\n");
 for(var i=1;i<licenseSplit.length;i++){
 var licenseDetails=licenseSplit[i].split(/\s+/);
 if ((licenseDetails[0].trim()=="securityk9" && licenseDetails[4].trim().toLowerCase()=="yes") || (licenseDetails[0].trim()=="advipservices" && licenseDetails[4].trim().toLowerCase()=="yes") || (licenseDetails[0].trim()=="advsecurity")) {
 found=true;
 break;
 }
 }
 try{
 xml = deviceCommunicator.getExecCmdOutput("show version | format " + deviceCommunicator.getInstallDir() + "/odm/overviewshVer.odm");
 version = $(xml).find('Version').text();
 ver = parseFloat(version);
 iosVer = ver.toFixed(1);
 if (found && iosVer > 15.3)
 return true;
 else
 return false;
 }
 catch(e){
 //consoleLog(e);
 }

 }*/

function loadPage() {
  //consoleLogMethodDetailsStart("frames.js", "loadPage()");

  var first = getUrlVariables()["feature"];
  utmDashboard.terminateCliWorker();
  switch (first) {
    case 'interface':
      $.get('iAndC.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          iAndC.iAndCLoading();
          $.unblockUI();
          $('ul#bottomnav li#bottomnav-1 a').addClass('toggleopacity');
          $('#hideAll').css('display', 'none');
          //setTimeout(openGoogleAnalyticsDialog(), 3000);
        }
      );
      break;
    case 'dhcpDns':
      $.get('dhcpDns.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          dhcpDns.dhcpDnsLoading();
          $.unblockUI();
          $('ul#bottomnav li#bottomnav-2 a').addClass('toggleopacity');
          $('#hideAll').css('display', 'none');
          //setTimeout(openGoogleAnalyticsDialog(), 3000);
        }
      );
      break;
    case 'user':
      $.get('user.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          userFeature.userFeatureLoading();
          $.unblockUI();
          $('ul#bottomnav li#bottomnav-3 a').addClass('toggleopacity');
          $('#hideAll').css('display', 'none');
          //setTimeout(openGoogleAnalyticsDialog(), 3000);
        }
      );
      break;
    case 'staticrouting':
      $.get('staticRouting.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          staticRouting.staticRoutingLoading();
          $.unblockUI();
          $('ul#bottomnav li#bottomnav-4 a').addClass('toggleopacity');
          $('#hideAll').css('display', 'none');
          //setTimeout(openGoogleAnalyticsDialog(), 3000);
        }
      );
      break;
    case 'routerdiagonstics':
      $.get('overview.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          $.unblockUI();
          overview.dashboardLoadingAll();

          $('ul#bottomnav li#bottomnav-5 a').addClass('toggleopacity');
          $('#hideAll').css('display', 'none');
          //setTimeout(openGoogleAnalyticsDialog(), 3000);
          enableDisableDashboard();
        }
      );
      break;
/*
    case 'ce':
      $.get('ceServer.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          ceServer.ceServerLoading();
          $.unblockUI();
          $('ul#bottomnav li#bottomnav-6 a').addClass('toggleopacity');
          $('#hideAll').css('display', 'none');
          //setTimeout(openGoogleAnalyticsDialog(), 3000);
        }
      );
      break;
*/
    case 'troubleshoot':
      $.get('pingAndTrace.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          pingAndTrace.pingAndTraceLoading();
          $.unblockUI();
          $('ul#bottomnav li#bottomnav-7 a').addClass('toggleopacity');
          $('#hideAll').css('display', 'none');
          //setTimeout(openGoogleAnalyticsDialog(), 3000);
        }
      );
      break;
    case 'anycli':
      $.get('transportCLI.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          transportCLI.transportCLILoading();
          $.unblockUI();
          $('ul#bottomnav li#bottomnav-8 a').addClass('toggleopacity');
          $('#hideAll').css('display', 'none');
          //setTimeout(openGoogleAnalyticsDialog(), 3000);
        }
      );
      break;
    case 'wireless':
      $.get('wireless.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          wireless.wirelessLoading();
          $.unblockUI();
          $('ul#bottomnav li#bottomnav-9 a').addClass('toggleopacity');
          $('#hideAll').css('display', 'none');
          //setTimeout(openGoogleAnalyticsDialog(), 3000);
        }
      );
      break;
    case 'acl':
      $.get('acl.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          acl.aclLoading();
          $.unblockUI();
          $('ul#bottomnav li#bottomnav-12 a').addClass('toggleopacity');
          $('#hideAll').css('display', 'none');
          //setTimeout(openGoogleAnalyticsDialog(), 3000);
        }
      );
      break;

    case 'phonehome':
      $.get('phonehome.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          phonehome.phoneHomeLoading();
          $.unblockUI();
          $('ul#bottomnav li#bottomnav-10 a').addClass('toggleopacity');
          $('#hideAll').css('display', 'none');
          //(openGoogleAnalyticsDialog(), 3000);
        }
      );
      break;

    case 'reset':
    case 'upgradeCCP':
      $.get('upgradeCCP.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          upgradeCCP.upgradeCCPLoading(first);
          $.unblockUI();
          $('#hideAll').css('display', 'none');
          //setTimeout(openGoogleAnalyticsDialog(), 3000);
        }
      );
      break;
     case 'upgradeIOS':
      $.get('upgradeIOS.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          upgradeCCP.upgradeCCPLoading(first);
          $.unblockUI();
          $('#hideAll').css('display', 'none');
          //setTimeout(openGoogleAnalyticsDialog(), 3000);
        }
      );
      break;
    case 'security':
      $.get('utm.html',
        function(data) {
          $('#content').html(data);
          $('#hideAll').css('display', 'block');
          if (!licenseCheck && iosk9check == "staticNatEnable") {
            //code
            utm.utmLoading(5);
          } else {
            utm.utmLoading(0);
          }
          $.unblockUI();
          $('ul#bottomnav li#bottomnav-11 a').addClass('toggleopacity');
          $('#hideAll').css('display', 'none');
          //setTimeout(openGoogleAnalyticsDialog(), 3000);
        }
      );
  }

  //consoleLogMethodDetailsEnd("frames.js", "loadPage()");

}

/***********************To do Internationalization***********************************/
function loadAndDisplayLanguages() {

  //consoleLogMethodDetailsStart("frames.js", "loadAndDisplayLanguages()");
  var hpDnsTitledhcpDnsHname = $.i18n.prop("basicSettingsTitle");
  var srSR = $.i18n.prop("SR");
  var cnsCNS = $.i18n.prop("CNS");
  var troubleshootTroubleshoot = $.i18n.prop("Troubleshoot");

  $("#dhcpDnsHname").text(hpDnsTitledhcpDnsHname);
  $("#SR").text(srSR);
  //$("#CNS").text(cnsCNS);
  $("#Troubleshoot").text(troubleshootTroubleshoot);

  var languageLocale = $.i18n.prop("langwage");
  if (languageLocale === "ja") {
//    var dhcpdnsArr = hpDnsTitledhcpDnsHname.split(" ");
//    $("#dhcpDnsHname").text("DHCP / DNS /");
//    $("#dhcpDnsHname1").text(dhcpdnsArr[4]);

    var srArr = srSR.split(" ");
    $("#SR").text(srArr[0]);
    $("#SR1").text(srArr[1]);

    //var cnsArr = cnsCNS.split(" ");
    //$("#CNS").text(cnsArr[0]);
    //$("#CNS1").text(cnsArr[1]);

    var trblshtArr = troubleshootTroubleshoot.split(" ");
    $("#Troubleshoot").text(trblshtArr[0]);
    $("#Troubleshoot1").text(trblshtArr[1]);
  }

  $("#ifcs").text($.i18n.prop("ifcs"));
  $("#HDname").text($.i18n.prop("HDname"));
  $("#UserMngmt").text($.i18n.prop("UserMngmt"));
  $("#DB").text($.i18n.prop("DB"));
  $("#ConfigCLI").text($.i18n.prop("ConfigCLI"));
  $("#Wireless").text($.i18n.prop("Wireless"));
  $("#PhoneHome").text($.i18n.prop("PhoneHome"));
  $("#framesClickForHelp").text($.i18n.prop("clickForHelpStr"));
  $("#framesViewQuickDemo").text($.i18n.prop("viewQuickDemoStr"));
  $("#Security").text($.i18n.prop("Security"));
  $("#framesClickForHelp").text($.i18n.prop("framesClickForHelp"));
  $("#framesClickForHelp1").text($.i18n.prop("framesClickForHelp1"));
  $("#framesViewQuickDemo").text($.i18n.prop("framesViewQuickDemo"));
  //$("#ui-id-1").text($.i18n.prop("googleAnalyticsPopUp"));
  //$("#googleAnalyticsPopUp").attr("title", $.i18n.prop("googleAnalyticsPopUp"));
  $("#analyticsInfoMessOne").text($.i18n.prop("analyticsInfoMessOne"));
  $("#analyticsInfoMessTwo").text($.i18n.prop("analyticsInfoMessTwo"));
  $("#analyticsInfoMessThree").text($.i18n.prop("analyticsInfoMessThree"));
  $("#analyticsInfoMessFour").text($.i18n.prop("analyticsInfoMessFour"));
  $("#analyticsInfoMessFive").text($.i18n.prop("analyticsInfoMessFive"));
  $(".moreOptions").text($.i18n.prop("moreOptions"));
  $('.popUpMenuItem[data="upgrade"] .popUpMenuText').text($.i18n.prop("ccpUpgrade"));
  $('.popUpMenuItem[data="updateIOS"] .popUpMenuText').text($.i18n.prop("IosUpdate"));
  $('.popUpMenuItem[data="reset"] .popUpMenuText').text($.i18n.prop("menuBackup"));
  $('.popUpMenuItem[data="preference"] .popUpMenuText').text($.i18n.prop("menuPreference"));
  $('.popUpMenuItem[data="caa"] .popUpMenuText').text($.i18n.prop("menuActiveAdvisor"));
  $('.popUpMenuItem[data="help"] .popUpMenuText').text($.i18n.prop("menuHelp"));
  $('.popUpMenuItem[data="feedback"] .popUpMenuText').text($.i18n.prop("menuFeedback"));

  //consoleLogMethodDetailsEnd("frames.js", "loadAndDisplayLanguages()");

}


$(document).ready(function() {
  loadAndDisplayLanguages();
  $('#ccpFrames').show();
  $('#bottomnav-9').hide();
  $('#bottomnav-11').hide();
  blockPage("Loading");
  var xml;
  //var visible = false;
  //$("#framesFadeInbox").hide();
  $(".inputnotallowspace").live("keypress", function(e) {
      if (e.which === 32){
        e.preventDefault();
      }
    });
  $(window).keydown(function(event) {
    if ((event.keyCode == 13)) {
      if (event.target.id == "cliInput") {
        //code
      } else {
        event.preventDefault();
        return false;
      }
    }
  });
  setTimeout(function() {

    loadPage();
  }, 1000);
  var arrval = [], ccpexpVersion;
  if (ccpExpressVersionValue!= "ccpexpressTextversion") {
    ccpexpVersion = ccpExpressVersionValue;
  } else {
    readVal = deviceCommunicator.readFromTemplate("version.txt", arrval, true);
    versionText = readVal.split(/\s+/);
    ccpexpVersion = versionText[2];
  }

  //$("#display").html("Provide feedback<br/> Version "+ccpexpVersion);
  //$("#display").html($.i18n.prop("provideFeed") + "<br/> " + $.i18n.prop("version") + " " + ccpexpVersion);


  /*$("#feedback").hover(function() {
    $("#display").slideDown(500);
  }, function() {
    $("#display").slideUp();
  });*/

  $('#moreMenuOptions').click(function(){
    $('.popUpMenuDiv').fadeToggle("fast",function() {
    $(this).css("overflow","visible");
    });
});
  //$('.popUpMenuVersion').text(($.i18n.prop("version") + " " + ccpexpVersion));
  $('#versionBoxNo').text($.i18n.prop("version"));
  $('#buildVersionNumber').text(ccpexpVersion);
  $('.popUpMenuItem').click(function(){
    $('.popUpMenuDiv').fadeToggle();
    if ($(this).attr("data")=="upgrade") {
  $.get('upgradeCCP.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              upgradeCCP.upgradeCCPLoading("upgradeCCP");
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
            $.unblockUI();
          }, 1000);
        }
      );
      $.unblockUI();
      //openGoogleAnalyticsDialog();
      history.pushState({}, '', "frames.html?feature=upgradeCCP");
    }
  else if ($(this).attr("data")=="updateIOS") {
    $.get('upgradeIOS.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              upgradeCCP.upgradeCCPLoading("upgradeIOS");
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
            $.unblockUI();
          }, 1000);
        }
      );
      $.unblockUI();
      //openGoogleAnalyticsDialog();
      history.pushState({}, '', "frames.html?feature=upgradeIOS");
  }else if ($(this).attr("data")=="feedback") {
  window.open("https://www.ciscofeedback.vovici.com/se.ashx?s=6A5348A77E0CDC49");
    }else if ($(this).attr("data")=="help") {
  window.open("http://www.cisco.com/c/en/us/td/docs/net_mgmt/cisco_configuration_professional_express/v3_3/guides/featureguide/ccp_express_Feature_Guide.html");
    }else if ($(this).attr("data")=="caa") {
  $.get('phonehome.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
            if (!($('ul#bottomnav li#bottomnav-10 a').hasClass('toggleopacity'))) {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              phonehome.phoneHomeLoading();
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
              $('ul#bottomnav li#bottomnav-10 a').addClass('toggleopacity');
            }
            $.unblockUI();
          }, 1000);
        }
      );
      $.unblockUI();
      //openGoogleAnalyticsDialog();
      history.pushState({}, '', "frames.html?feature=phonehome");
    }else if ($(this).attr("data")=="preference") {
  $('#preferencesDialog').dialog("open");
  worker = new Worker('../js/settingsWorker.js');
    }else if ($(this).attr("data")=="reset") {
  $.get('upgradeCCP.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              upgradeCCP.upgradeCCPLoading("reset");
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
    $.unblockUI();
          }, 1000);
        }
      );
      $.unblockUI();
      history.pushState({}, '', "frames.html?feature=reset");
    }


    });


  xml = deviceCommunicator.getExecCmdOutput("show ip interface brief");
  if (xml.toLowerCase().indexOf('wlan') !== -1 || xml.toLowerCase().indexOf('wlan') !== -1) {
    $('#bottomnav-9').show();
  }
  //licenseCheck=checkSecurityLicense();
  if (!licenseCheck) {

    if (iosk9check == "SecurityEnable" || iosk9check == "staticNatEnable") {
      $('#bottomnav-11').show();
    } else {
      $('#bottomnav-11').hide();
    }
  } else {
    $('#bottomnav-11').show();
  }
  $('ul#bottomnav li#bottomnav-1 a').each(function() {
    $(this).click(function() {
      $.get('iAndC.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
            if (!($('ul#bottomnav li#bottomnav-1 a').hasClass('toggleopacity'))) {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              iAndC.iAndCLoading();
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
              $('ul#bottomnav li#bottomnav-1 a').addClass('toggleopacity');
            }
            $.unblockUI();
            //setTimeout(openGoogleAnalyticsDialog(), 3000);
          }, 1000);
        }
      );
      $.unblockUI();
      history.pushState({}, '', "frames.html?feature=interface");
    });
  });
  $('ul#bottomnav li#bottomnav-2 a').each(function() {
    $(this).click(function() {
      $.get('dhcpDns.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
            if (!($('ul#bottomnav li#bottomnav-2 a').hasClass('toggleopacity'))) {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              dhcpDns.dhcpDnsLoading();
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
              $('ul#bottomnav li#bottomnav-2 a').addClass('toggleopacity');
            }
            $.unblockUI();
            //setTimeout(openGoogleAnalyticsDialog(), 3000);
          }, 1000);
        }
      );
      $.unblockUI();
      history.pushState({}, '', "frames.html?feature=dhcpDns");
    });
  });
  $('ul#bottomnav li#bottomnav-3 a').each(function() {
    $(this).click(function() {
      $.get('user.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
            if (!($('ul#bottomnav li#bottomnav-3 a').hasClass('toggleopacity'))) {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              userFeature.userFeatureLoading();
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
              $('ul#bottomnav li#bottomnav-3 a').addClass('toggleopacity');
            }
            $.unblockUI();
            //setTimeout(openGoogleAnalyticsDialog(), 3000);
          }, 1000);
        }
      );
      $.unblockUI();
      history.pushState({}, '', "frames.html?feature=user");
    });
  });
  $('ul#bottomnav li#bottomnav-4 a').each(function() {
    $(this).click(function() {
      $.get('staticRouting.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
            if (!($('ul#bottomnav li#bottomnav-4 a').hasClass('toggleopacity'))) {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              staticRouting.staticRoutingLoading();
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
              $('ul#bottomnav li#bottomnav-4 a').addClass('toggleopacity');
            }
            $.unblockUI();
            //setTimeout(openGoogleAnalyticsDialog(), 3000);
          }, 1000);
        }
      );
      $.unblockUI();
      history.pushState({}, '', "frames.html?feature=staticrouting");
    });
  });
  $('ul#bottomnav li#bottomnav-5 a').each(function() {
    $(this).click(function() {
      $.get('overview.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
            if ($('ul#bottomnav li#bottomnav-5 a').hasClass('toggleopacity')) {
              $('ul#bottomnav li#bottomnav-5 a').removeClass('toggleopacity')
            }
            if (!($('ul#bottomnav li#bottomnav-5 a').hasClass('toggleopacity'))) {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              $.unblockUI();
              overview.dashboardLoadingAll(0, "");
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
              $('ul#bottomnav li#bottomnav-5 a').addClass('toggleopacity');
              enableDisableDashboard();
              //setTimeout(openGoogleAnalyticsDialog(), 5000);

            }

          }, 1000);
        }
      );
      $.unblockUI();
      history.pushState({}, '', "frames.html?feature=routerdiagonstics");
    });
  });

  /*
  $('ul#bottomnav li#bottomnav-6 a').each(function() {
    $(this).click(function() {
      $.get('ceServer.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
            if (!($('ul#bottomnav li#bottomnav-6 a').hasClass('toggleopacity'))) {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              ceServer.ceServerLoading();
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
              $('ul#bottomnav li#bottomnav-6 a').addClass('toggleopacity');
            }
            $.unblockUI();
          }, 1000);
        }
      );
      $.unblockUI();
      //openGoogleAnalyticsDialog();
      history.pushState({}, '', "frames.html?feature=ce");
    });
  });
  */
  $('ul#bottomnav li#bottomnav-7 a').each(function() {
    $(this).click(function() {
      $.get('pingAndTrace.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
            if (!($('ul#bottomnav li#bottomnav-7 a').hasClass('toggleopacity'))) {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              pingAndTrace.pingAndTraceLoading();
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
              $('ul#bottomnav li#bottomnav-7 a').addClass('toggleopacity');
            }
            $.unblockUI();
          }, 1000);
        }
      );
      $.unblockUI();
      //openGoogleAnalyticsDialog();
      history.pushState({}, '', "frames.html?feature=troubleshoot");
    });
  });
  $('ul#bottomnav li#bottomnav-8 a').each(function() {
    $(this).click(function() {
      $.get('transportCLI.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
            if (!($('ul#bottomnav li#bottomnav-8 a').hasClass('toggleopacity'))) {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              transportCLI.transportCLILoading();
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
              $('ul#bottomnav li#bottomnav-8 a').addClass('toggleopacity');
            }
            $.unblockUI();
          }, 1000);
        }
      );
      $.unblockUI();
      //openGoogleAnalyticsDialog();
      history.pushState({}, '', "frames.html?feature=anycli");
    });
  });
  $('ul#bottomnav li#bottomnav-9 a').each(function() {
    $(this).click(function() {
      $.get('wireless.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
            if (!($('ul#bottomnav li#bottomnav-9 a').hasClass('toggleopacity'))) {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              wireless.wirelessLoading();
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
              $('ul#bottomnav li#bottomnav-9 a').addClass('toggleopacity');
            }
            $.unblockUI();
          }, 1000);
        }
      );
      $.unblockUI();
     // openGoogleAnalyticsDialog();
      history.pushState({}, '', "frames.html?feature=wireless");
    });
  });


  $('ul#bottomnav li#bottomnav-10 a').each(function() {
    $(this).click(function() {
      $.get('phonehome.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
            if (!($('ul#bottomnav li#bottomnav-10 a').hasClass('toggleopacity'))) {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              phonehome.phoneHomeLoading();
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
              $('ul#bottomnav li#bottomnav-10 a').addClass('toggleopacity');
            }
            $.unblockUI();
          }, 1000);
        }
      );
      $.unblockUI();
      //openGoogleAnalyticsDialog();
      history.pushState({}, '', "frames.html?feature=phonehome");
    });
  });


  $('ul#bottomnav li#bottomnav-11 a').each(function() {
    $(this).click(function() {
      $.get('utm.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
            if (!($('ul#bottomnav li#bottomnav-11 a').hasClass('toggleopacity'))) {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              utmDashboard.terminateCliWorker();
              if (!licenseCheck && iosk9check == "staticNatEnable") {
                utm.utmLoading(5);
              } else {
                utm.utmLoading(0);
              }
              //utm.utmLoading();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
              $('ul#bottomnav li#bottomnav-11 a').addClass('toggleopacity');
            }
            $.unblockUI();
          }, 1000);
        }
      );
      $.unblockUI();
      //openGoogleAnalyticsDialog();
      history.pushState({}, '', "frames.html?feature=security");
    });
  });
  $('ul#bottomnav li#bottomnav-12 a').each(function() {
    $(this).click(function() {
      $.get('acl.html',
        function(data) {
          blockPage("Loading");
          setTimeout(function() {
            if (!($('ul#bottomnav li#bottomnav-12 a').hasClass('toggleopacity'))) {
              $('#content').html(data);
              $('#hideAll').css('display', 'block');
              acl.aclLoading();
              utmDashboard.terminateCliWorker();
              $('#hideAll').css('display', 'none');
              $('ul#bottomnav li a').removeClass('toggleopacity');
              $('ul#bottomnav li#bottomnav-12 a').addClass('toggleopacity');
            }
            $.unblockUI();
          }, 1000);
        }
      );
      $.unblockUI();
      //openGoogleAnalyticsDialog();
      history.pushState({}, '', "frames.html?feature=acl");
    });
  });
  /*$("#googleAnalyticsPopUp").dialog({
    autoOpen: false,
    height: 490,
    width: 675,
    modal: true,
    buttons: [{
        text: $.i18n.prop("yes"),
        click: function() {
          SetCookie(name, 'true', expiry);
          getGATrackCode();
          $(this).dialog("close");
        }
      }, {
        text: $.i18n.prop("no"),
        click: function() {
          SetCookie(name, 'false', expiry);
          $(this).dialog("close");
        },
      }],
    close: function() {
      if (GetCookie(name) == null || GetCookie(name) == "undefined") {
        if (isCookiesEnabled()) {
          SetCookie(name, 'false', expiry);
        }
      }
    }
  });*/

});

/*function blockui with loading icon */
function blockPage(msg) {
  //consoleLogMethodDetailsStart("frames.js", "blockPage()");

  $.blockUI({
    css: {
      border: 'none',
      backgroundColor: 'none'
    },
    message: '<div class="loading_container"><div class="loading_ring loading_blue"></div><div id="loading_content"><span>' +
              $.i18n.prop(msg) + '</span></div></div>'
  });
  //consoleLogMethodDetailsEnd("frames.js", "blockPage()");
}
/* main checkbox selection*/
$('thead input:checkbox').live('click', function() {
  var $currentTable = $(this).closest("tr").parents('table');
  var tableId = $currentTable.attr("id");
  if ($(this).is(":checked")) {
    $currentTable.find('tbody input:checkbox').not(":disabled").attr('checked', 'checked');
    $("#" + tableId + " tbody tr").addClass("hilite");
  } else {
    $currentTable.find('tbody input:checkbox').removeAttr('checked');
    $currentTable.find('tbody input:checkbox').closest("tr").removeClass("hilite");
    $currentTable.find('tbody input:checkbox').closest("tr").siblings().removeClass('hilite');
    $currentTable.find('tbody input:checkbox').parents("table").find('tr').each(function(){
      $(this).removeClass('hilite');
    })
  }
  if (tableId == "dhcpTable") {
    enableDisableButton(tableId, $.i18n.prop("Add"));
  } else if (tableId == "groupTable") {
    enableDisableButton(tableId, "add-group");
  } else if (tableId == "userTable") {
    enableDisableButton(tableId, "add-user");
  } else if (tableId == "staticroutingtable") {
    $("#" + tableId + " tbody tr:first").removeClass("hilite");
    enableDisableButton(tableId, "add");
  } else if (tableId == "securityPolicytable") {
    enableDisableButton(tableId, "add");
  } else if (tableId == "natTable") {
    enableDisableButton(tableId, "addNat");
  }else if (tableId == "aclTable") {
    //enableDisableButton(tableId, "aclAdd");
    if ($(this).is(":checked")) {
      $("#interfaceACL").hide();
      $("#addACL").hide();
      $("#cloneACL").hide();
    } else {
    $("#addACL").show();
    $("#cloneACL").show();
    }
  }
});

$('tbody input:checkbox').parents("table").find('tr').each(function(){
      console.log($(this).html());
      $(this).removeClass('hilite');
    })

$('tbody input:checkbox').live('click', function() {
  var $this = $(this);
  var tableId = $this.closest("tr").parents('table').attr("id");
  if ($("#" + tableId).hasClass("tblClick")) {
    if ($this.is(":checked")) {
      $this.closest("tr").addClass("hilite");
    } else {
      $this.closest("tr").removeClass("hilite");
      $("thead input:checkbox").prop('checked', false);
    }
  }
  var tableLength = $('#' + tableId + ' tbody tr').length;
  var tableSelectedRows = $('#' + tableId + ' tbody input:checkbox:checked').length;
  if (tableLength == tableSelectedRows) {
    $("thead input:checkbox").prop('checked', true);
  }
  if (tableId == "dhcpTable") {
    enableDisableButton(tableId, "Add");
  } else if (tableId == "groupTable") {
    enableDisableButton(tableId, "add-group");
  } else if (tableId == "userTable") {
    enableDisableButton(tableId, "add-user");
  } else if (tableId == "staticroutingtable") {
    enableDisableButton(tableId, "add");
  } else if (tableId == "securityPolicytable") {
    enableDisableButton(tableId, "add");
  } else if (tableId == "natTable") {
    enableDisableButton(tableId, "addNat");
  }else if (tableId == "aclTable") {
    enableDisableButton(tableId, "aclacl");
  }
});
/*function to add checkbox and edit,delete icons*/
function addTableColumn(id, editClass, deleteClass) {
  //consoleLogMethodDetailsStart("frames.js", "addTableColumn()");
  $('#' + id).find('tr').each(function() {
    if ($(this).hasClass('policyhead')) {
      isEmptyBlock = true;
    } else {
      $(this).find('td').eq(0).before('<td><input type = "checkbox" /></td>');
      if (id == "userTable" || id == "groupTable") {
        //$(this).find('td:last').after('<td><span  class="fa fa-trash-o '+deleteClass+'  ccpexpCSSReplaceClass738" title="Delete"/></td>');
        $(this).find('td:last').after('<td><span  class="fa fa-trash-o ' + deleteClass + '  ccpexpCSSReplaceClass739" title="'
                                      + $.i18n.prop("delete") + '"/></td>');
      } else if ($(this).hasClass('read_only')) {
        //$(this).find('td:last').after('<td align="right"><span  class="fa fa-trash-o '+deleteClass+'  ccpexpCSSReplaceClass740" title="Delete"/></td>');
        $(this).find('td:last').after('<td align="right"><span  class="fa fa-trash-o ' + deleteClass + '  ccpexpCSSReplaceClass741" title="' +
                                      $.i18n.prop("delete") + '"/></td>');
      } else {
        //$(this).find('td:last').after('<td class="ccpexpCSSReplaceClass742">'+
        //                              '<span  class="fa fa-pencil-square-o '+editClass+' ccpexpCSSReplaceClass743" title="Edit" />'+
        //                              '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span  class="fa fa-trash-o '+deleteClass+'  ccpexpCSSReplaceClass744" title="Delete"/></td>');
        $(this).find('td:last').after('<td class="ccpexpCSSReplaceClass745 editDeleteAligning" >'+
                                      '<span  class="fa fa-pencil-square-o ' + editClass + '  ccpexpCSSReplaceClass746" title="' +
                                      $.i18n.prop("edit") +
                                      '" />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+
                                      '<span  class="fa fa-trash-o ' + deleteClass + '  ccpexpCSSReplaceClass747" title="' +
                                      $.i18n.prop("delete") + '"/></td>');
      }
    }
  });
  //consoleLogMethodDetailsEnd("frames.js", "addTableColumn()");
}

/*function to add the delete buttonm alone in acl */
function addDeleteTableColumn(id, deleteClass) {
  //consoleLogMethodDetailsStart("frames.js", "addTableColumn()");
  $('#' + id).find('tr').each(function() {
    if ($(this).hasClass('policyhead')) {
      isEmptyBlock = true;
    } else {
      //$(this).find('td').eq(0).before('<td><input type = "checkbox" /></td>');
      if (id == "bindTable") {
        //$(this).find('td:last').after('<td><span  class="fa fa-trash-o '+deleteClass+'  ccpexpCSSReplaceClass738" title="Delete"/></td>');
        $(this).find('td:last').after('<td><span  class="fa fa-trash-o ' + deleteClass + '  ccpexpCSSReplaceClass739" title="'
                                      + $.i18n.prop("delete") + '"/></td>');
      }
    }
  });
  //consoleLogMethodDetailsEnd("frames.js", "addTableColumn()");
}

/*disable edit/delete button*/
function changeBtnState(tableId, buttonId) {
  //consoleLogMethodDetailsStart("frames.js", "changeBtnState()");
  var chkboxChecked;
  $('#' + tableId + ' tr').on('click', (function() {
    setTimeout(function() {
      chkboxChecked = $("#" + tableId + " tbody input:checkbox:checked").length;
      if (chkboxChecked > 1) {
        $("#" + buttonId).addClass("ui-state-disabled");
        $("#" + buttonId).attr("disabled", true);
      } else {
        $("#" + buttonId).removeClass("ui-state-disabled");
        $("#" + buttonId).attr("disabled", false);
      }
    }, 100);
  }));
  //consoleLogMethodDetailsEnd("frames.js", "changeBtnState()");
}

/* enable/diable add button*/
function enableDisableButton(tableId, buttonId) {
  //consoleLogMethodDetailsStart("frames.js", "enableDisableButton()");
  if ($("#" + tableId + " tbody tr").hasClass("hilite")) {
    $("#" + buttonId).addClass("ui-state-disabled");
    $("#" + buttonId).attr("disabled", true);
  } else {
    $("#" + buttonId).removeClass("ui-state-disabled");
    $("#" + buttonId).attr("disabled", false);
  }
  //consoleLogMethodDetailsEnd("frames.js", "enableDisableButton()");
}

