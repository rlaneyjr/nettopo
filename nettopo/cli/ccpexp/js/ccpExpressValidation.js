$(document).ready(function() {

  loadAndDisplayValidationMsgs();

  /***************CLASSES that can be added to attain validations on GUI*******************************/

// To validate IPv4 address
  $.validator.addClassRules({
    requiredipv4: {required: true, ipv4: true}
  });

// To validate IPv6 address
  $.validator.addClassRules({
    requiredipv6: {required: true, ipv6: true}
  });

// To validate IPv4 address for DHCP-DNS module
  $.validator.addClassRules({
    notrequiredipv4: {ipv4: true}
  });

// To validate IPv4 Prefix address it validates 0.0.0.0 as well
  $.validator.addClassRules({
    requiredIPv4Prefix: {required: true, validPrefixAddress: true}
  });

// To validate input can be both IPv4 or IPv6 address
  $.validator.addClassRules({
    requiredIPv4IPv6Address: {ipv4oripv6: true}
  });

// To validate Prefix and Prefix Mask values are in sync with each other
  $.validator.addClassRules({
    requiredIPv4PrefixAndPrefixMask: {required: true, validPrefixMaskAddress: true, validPrefixAndPrefixMask: true}
  });
// To validate  IPv4 Subnet Mask values
  $.validator.addClassRules({
    requiredIPv4SubnetMask: {required: true, validPrefixMaskAddress: true}
  });

// To validate Prefix Mask values are within a given range(0-128)
  //$.validator.addClassRules({
  //  requiredIPv6PrefixAndPrefixMask: {required: true, range: [0, 128]}
  //});

  $.validator.addClassRules({
    requiredIPv6PrefixAndPrefixMask: {required: true, validIpv6Range:true}
  });

  $.validator.addClassRules({
    checkVlanIdIsInRange: {required: true, validVLANID1To4094:true}
  });


//To validate Poolname - permitting only ALPHABETS and NUMBERS
  $.validator.addClassRules({
    requiredPoolName: {required: true, nameCheck: true}
  });

//To validate VPI lies between the range of  - 0 to 31 (inclusive)
  $.validator.addClassRules({
    requiredVPI: {range: [0, 31]}
  });
//To validate VCI lies between the range of  - 1 to 1023 (inclusive)
  $.validator.addClassRules({
    requiredVCI: {range: [1, 1023]}
  });

//To validate VLanID lies between the range of  - 1 to 4094 (inclusive) excluding (1002 to 1005 inclusive)
  $.validator.addClassRules({
    requiredVlanRange: {range: [1, 4094], validVLanID: true}
  });

//To validate CNS HostNname - with two dots and three values, excluding special characters except "-"
  $.validator.addClassRules({
    requiredCNShostname: {required: true, validCNShostname: true}
  });

//To validate GSM Profile creation - excluding special character "?"
  $.validator.addClassRules({
    requiredAPNUserPswd: {required: true, validAPNUserPswd: true}
  });

//To validate OTASP Phone No. - with digits or '*' or '#'
  $.validator.addClassRules({
    requiredOTASPPhoneNo: {required: true, validOTASPPhoneNo: true}
  });

  $.validator.addClassRules({
    requiredHexaKeyValue: {required: true, validHexaKeyValue: true}
  });

  $.validator.addClassRules({
    requiredHexaKeyValueCheck: {required: true, validHexaKeyValueCheck: true}
  });

  $.validator.addClassRules({
    requiredHexaKeyValueLength: {required: true, validHexaKeyValueLength: true}
  });
  $.validator.addClassRules({
    requiredBaseDn: {required: true, basedn: true}
  });
  $.validator.addClassRules({
    requiredEncryptHexaKeyValue: {required: true, validEncryptHexaKeyValueLength: true}
  });

//To validate autonomous number lies between the range of  - 1 to 65535 (inclusive)
  $.validator.addClassRules({
    requiredAutoKeyRangeVPN: {required: true, validAutonomousKey: true}
  });
//To validate tunnel ip, backup tunnel ip and remote tunnel ip of dmvpn in the same subnet.
  $.validator.addClassRules({
    requiredTipRipSameSubnet: {required: true, validTunnelSubnet: true}
  });
//To validate tunnel ip, backup tunnel ip, Transport address and remote tunnel ip of dmvpn are not same.
  $.validator.addClassRules({
    requiredIsSameIpAddr: {required: true, validDistintIPAddrDmvpnSpoke: true}
  });

  $.validator.addClassRules({
    reqDiffPoolAddress: {required: true, ipv4:true, isDiffPoolAddress: true}
  });

  $.validator.addClassRules({
    reqSameSubnetPoolAddress: {required: true, isSameSubnetPoolAddress: true}
  });
  
  $.validator.addClassRules({
    reqToAddrGreaterThanFromAddr: {required: true, isToAddrGreaterThanFromAddr: true}
  });
  
  
//To validate tunnel ip and backup tunnel is in the same subnet DMVPN
  $.validator.addClassRules({
    requiredSameSubnetDmvpn: {required: true, validTunnelBackupMaskDmvpn: true}
  });
//To validate tunnel ip and backup tunnel is in the same subnet IPSEC
  $.validator.addClassRules({
    requiredSameSubnet: {required: true, validTunnelBackupMask: true}
  });
  $.validator.addClassRules({
    requiredHubSameSubnet: {required: true, validHubTunnelBackupMask: true}
  });
  //To validate DHCP Pool
  $.validator.addClassRules({
    requiredDHCPPool: {required: true, validateDHCPPool: true}
  });
  //To validate Source Port and Destination port in ACL
  $.validator.addClassRules({
    requiredAutoKeyRange: {required: true, validPortCheck: true}
  });
  /************************************BELOW code is related to validations *********************************/

  /*******Calling the  JavaScript functions and printing the appropriate correction messages************/

  $.validator.addMethod("ipv4", function(value, element) {
    return validateIpv4Address(value);
  }, $.i18n.prop("validateIpv4Address"));

  $.validator.addMethod("validIpSubnet", function(value, element) {
    return isValidIpSubnet(value, element);
  }, $.i18n.prop("isValidIpSubnet"));

  $.validator.addMethod("validVLANID1To4094", function(value, element) {
    return isValidVLANID(value);
  }, $.i18n.prop("vlanIDError"));

  $.validator.addMethod("validIpAndSubnetId", function(value, element) {
    return isValidSubnetId(value, element);
  }, $.i18n.prop("isValidSubnetId"));

  $.validator.addMethod("ipv6", function(value, element) {
    return validateIpv6Address(value);
  }, $.i18n.prop("validateIpv6Address"));

  $.validator.addMethod("validIpv6Range", function(value, element) {
    return isValidIpv6Range(value);
  }, $.i18n.prop("ipv6Error"));

  $.validator.addMethod("ipv4oripv6", function(value, element) {
    return validateIpv4orIpv6Address(value);
  }, $.i18n.prop("validateIpv4orIpv6Address"));
  $.validator.addMethod("basedn", function(value, element) {
    return validateLdapDn(value);
  }, $.i18n.prop("validatebasedn"));

  $.validator.addMethod("nameCheck", function(value, element) {
    return onlyAlphabetsAndCharacters(value);
  }, $.i18n.prop("onlyAlphabetsAndCharacters"));

  $.validator.addMethod("validVLanID", function(value, element) {
    return excludeFromRange(value);
  }, $.i18n.prop("excludeFromRange"));

  $.validator.addMethod("validPrefixAddress", function(value, element) {
    return includeWildIPaddress(value);
  }, $.i18n.prop("includeWildIPaddress"));

  $.validator.addMethod("validPrefixMaskAddress", function(value, element) {
    return isValidSubnetMask(value);
  }, $.i18n.prop("isValidSubnetMask"));

  $.validator.addMethod("validPrefixAndPrefixMask", function(value, element) {
    return isPrefixAndPrefixMask(value);
  }, $.i18n.prop("isPrefixAndPrefixMask"));

  $.validator.addMethod("validPrefixAndPrefixMaskDmVPN", function(value, element) {
    return isPrefixAndPrefixMaskDmvpn(value);
  }, $.i18n.prop("isPrefixAndPrefixMaskDmvpn"));

  $.validator.addMethod("validDefaultRoutingAddress", function(value, element) {
    return isDefaultRouting(value);
  }, $.i18n.prop("isDefaultRouting"));

  $.validator.addMethod("validCNShostname", function(value, element) {
    return isCNShostname(value);
  }, $.i18n.prop("isCNShostname"));
  $.validator.addMethod("validOTASPPhoneNo", function(value, element) {
    return isOTASPPhoneNo(value);
  }, $.i18n.prop("isOTASPPhoneNo"));
  $.validator.addMethod("validAPNUserPswd", function(value, element) {
    return isAPNUserPswd(value);
  }, $.i18n.prop("isAPNUserPswd"));
  $.validator.addMethod("validHexaKeyValue", function(value, element) {
    return isHexaKeyValue(value);
  }, $.i18n.prop("isHexaKeyValue"));
  $.validator.addMethod("validHexaKeyValueCheck", function(value, element) {
    return isHexaKeyValueCheck(value);
  }, $.i18n.prop("isHexaKeyValueCheck"));
  $.validator.addMethod("validHexaKeyValueLength", function(value, element) {
    return isHexaKeyValueLength(value);
  }, $.i18n.prop("isHexaKeyValueLength"));
  $.validator.addMethod("validEncryptHexaKeyValueLength", function(value, element) {
    return isHexaKeyValueEncrypt(value);
  }, $.i18n.prop("isHexaKeyValueEncrypt"));
  $.validator.addMethod("validAutonomousKey", function(value, element) {
    return isValidAutonomousKey(value);
  }, $.i18n.prop("isValidAutonomousKey"));
  $.validator.addMethod("validTunnelSubnet", function(value, element) {
    var ip1 = $("#tunnelIp").val(),
      ip2 = $("#tunnelAddr").val(),
      ip3 = $("#backupTunnelIP").val(),
      mask = $("#tunnelMask").val();
    return configureVpn.isInSameSubnet(ip1, ip2, ip3, mask);
  }, $.i18n.prop("isInSameSubnet"));
  $.validator.addMethod("validTunnelBackupMask", function(value, element) {
    var ip1 = $("#s2sTunnelIP").val(),
      ip2 = $("#s2sBackupIP").val(),
      ip3 = "",
      mask = $("#s2sTunnelMask").val();
    return configureVpn.isInSameSubnet(ip1, ip2, ip3, mask);
  }, $.i18n.prop("validTunnelBackupMask"));
  $.validator.addMethod("validHubTunnelBackupMask", function(value, element) {
    var ip1 = $("#dmvpnTunnelIp").val(),
      ip2 = $("#hubBackupIP").val(),
      ip3 = "",
      mask = $("#dmvpnHubTunnelMask").val();
    return configureVpn.isInSameSubnet(ip1, ip2, ip3, mask);
  }, $.i18n.prop("validTunnelBackupMask"));
  $.validator.addMethod("validTunnelBackupMaskDmvpn", function(value, element) {
    var ip1 = $("#tunnelIp").val(),
      ip2 = $("#tunnelAddr").val(),
      ip3 = "",
      mask = $("#tunnelMask").val();
    return configureVpn.isInSameSubnet(ip1, ip2, ip3, mask);
  }, $.i18n.prop("validTunnelRemoteMask"));
  $.validator.addMethod("validDistintIPAddrDmvpnSpoke", function(value, element) {
    return configureVpn.isDistintIPAddrDmvpnSpoke();
  }, $.i18n.prop("ipAddressSpokeHubDistinctMessage"));
  $.validator.addMethod("validateDHCPPool", function(value, element) {
    return validateDHCPPool(value);
  }, $.i18n.prop("validateDHCPPool"));

  $.validator.addMethod("isDiffPoolAddress", function(value, element) {
    var ip1 = $("#remoteAddressPoolFrom").val();
    var ip2 = $("#remoteAddressPoolTo").val();
    return !configureVpn.isSameValue(ip1, ip2);
  }, $.i18n.prop("remoteAccessPoolRangeSameValError"));

  $.validator.addMethod("isSameSubnetPoolAddress", function(value, element) {
    var ip1 = $("#remoteAddressPoolFrom").val();
    var ip2 = $("#remoteAddressPoolTo").val();
    return !configureVpn.remoteAccessPoolValidation(ip1, ip2);
  }, $.i18n.prop("remoteAccessPoolRangeError"));

  $.validator.addMethod("isToAddrGreaterThanFromAddr", function(value, element) {
    var ip1 = $("#remoteAddressPoolFrom").val();
    var ip2 = $("#remoteAddressPoolTo").val();
    return !configureVpn.remoteAccessFromToValidation(ip1, ip2);
  }, $.i18n.prop("remoteAccessFromLessThanToError"));


    $.validator.addMethod("userInputCheck", function(value, element) {
    return userInputCheck(value, element);
  }, $.i18n.prop("userNameExists"));

  $.validator.addMethod("duplicatePoolCheck", function(value, element) {
    return duplicatePoolCheck(value, element);
  }, $.i18n.prop("poolExists"));
  $.validator.addMethod("validPortCheck", function(value, element) {
    return isPortValid(value);
  }, $.i18n.prop("isPortValid"));
});
/***************************************JAVA SCRIPT FUNCTIONS  for validations************************/


/*************************************To explicitly allow 0.0.0.0 for IPv4 Prefix IP address****************************************/

function includeWildIPaddress(ip) {
  var reg = /^([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3}$/i,
    wildReg = /^0.0.0.0$/;
  if (reg.test(ip) || wildReg.test(ip)) {
    return true;
  }
  else {
    return false;
  }


}
/******************************************************  To validate IPV4 *********************************************************/
function validateIpv4Address(ip) {
  var reg = /^([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3}$/i;
  if (ip !== "") {
    if (reg.test(ip)) {
      return true;
    }
    else {
      return false;
    }
  }
  else {
    return true;
  }
}

/*********************************************  To validate IP Address and Subnet mask combination ****************************************/



function isValidVLANID(vlanidstring) {
  var reg = /^([1-9]|[1-9][0-9]|[0-9][0-9][0-9]|[1-3][0-9][0-9][0-9]|40[0-9][0-4])$/;
  if (reg.test(vlanidstring)) {
    return true;
  }
  return false;

//  if(vlanidstring === parseInt(vlanidstring, 10) && vlanidstring>0 && vlanidstring<4095)
//  {
//    return true;
//  }
//  else
//  {
//    return false;
//  }
//  return false;
}

function isValidIpSubnet(subStr, element) {

var temp = $('input[data='+$(element).attr("id")+']');
var ipStr = temp.val();
var loop = "";
loop = $('input:hidden[name=loopy]').val();

if(subStr == "255.255.255.255" && (loop.toLowerCase().indexOf('loopback')===0))
{
  return true;
}
 else
 {
var ip = ipStr.split(".");
var sub = subStr.split(".");

var ip0 = parseInt(ip[0],10);
var ip1 = parseInt(ip[1],10);
var ip2 = parseInt(ip[2],10);
var ip3 = parseInt(ip[3],10);

var sub0 = parseInt(sub[0],10);
var sub1 = parseInt(sub[1],10);
var sub2 = parseInt(sub[2],10);
var sub3 = parseInt(sub[3],10);

var r0 = ip0 & sub0;
var r1 = ip1 & sub1;
var r2 = ip2 & sub2;
var r3 = ip3 & sub3;

var subnetId= r0+"."+r1+"."+r2+"."+r3;

var or0 = ip0 | getComplement(sub0);
var or1 = ip1 | getComplement(sub1);
var or2 = ip2 | getComplement(sub2);
var or3 = ip3 | getComplement(sub3);

var broadcastId= or0+"."+or1+"."+or2+"."+or3;

if((subnetId==ipStr && temp.attr("uncheck")!="network") || broadcastId==ipStr)
{
return false;
}
else{
return true;
}

 }
}
function getComplement(subs)
{
var a =0;
if(subs == 0)
{
a =255;
}
else if(subs< 255)
{
a= 1;
while(((subs>>>1)& 1) == 0)
{
a= (a << 1)|1;
subs= subs >>> 1;
}
}
return a;
}

/*************************************************** To return valid Subnet ID****************************************************/

function isValidSubnetId(subStr, element) {

var temp = $('input[data='+$(element).attr("id")+']');
var ipStr = temp.val();

var ip = ipStr.split(".");
var sub = subStr.split(".");

var ip0 = parseInt(ip[0],10);
var ip1 = parseInt(ip[1],10);
var ip2 = parseInt(ip[2],10);
var ip3 = parseInt(ip[3],10);

var sub0 = parseInt(sub[0],10);
var sub1 = parseInt(sub[1],10);
var sub2 = parseInt(sub[2],10);
var sub3 = parseInt(sub[3],10);

var r0 = ip0 & sub0;
var r1 = ip1 & sub1;
var r2 = ip2 & sub2;
var r3 = ip3 & sub3;

var subnetId= r0+"."+r1+"."+r2+"."+r3;
// alert("Subnet ID = "+subnetId);

if(subnetId==ipStr)
{
return true;
}
else{
return false;
}
}

/*********************************************  To validate IPV6 ****************************************/

function validateIpv6Address(ipv6) {
  var reg = /^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$/;
  if (reg.test(ipv6)) {
    return true;
  }
  return false;

}

function isValidIpv6Range(ipv6string) {
  var reg=/^([0-9]|[1-9][0-9]|1[01][0-9]|12[0-8])$/;
  if (reg.test(ipv6string)) {
    return true;
  }
//  if(ipv6string === parseInt(ipv6string, 10))
//  {
//    if(parseInt(ipv6string, 10)>-1 && parseInt(ipv6string, 10)<129)
//      return true;
//    else
//      return false;
//  }
//  else
//    return false;

  return false;
}

/********************************************To validate Base Dn in LDAP*******************************************/

function validateLdapDn(ldapDn) {
  if (typeof ldapDn === 'undefined') {
    return false;
  }
  var reg = /^(\w+[=]{1}\w+)([,{1}]\w+[=]{1}\w+)*$/;
  var ascapeChar = /\s+/g;
  var ascapeSpecial = /(['\_\-.*+?^!:${}()|\[\]\/\\])/g;
  var removeSpaces = ldapDn.replace(ascapeChar, '');
  var finalValue = removeSpaces.replace(ascapeSpecial, '');
  if (reg.test(finalValue)) {
    return true;
  }
  return false;
}
/********************************************To validate Base Dn in LDAP*******************************************/
function validateDHCPPool(poolName) {
  if (typeof poolName === 'undefined') {
    return false;
  }
  var poolNameValidate = $.trim(poolName);
  if ((!poolNameValidate) || poolNameValidate === 'select') {
    return false;
  }
  return true;
}
/*************************************To allow IPv4 or IPv6 address****************************************/

function validateIpv4orIpv6Address(ip) {
  if (validateIpv4Address(ip) || validateIpv6Address(ip) || ip === "") {
    return true;
  } else {
    return false;
  }
}


/*******************  To validate value in a textbox should be only alphabets and special characters********************************/
function onlyAlphabetsAndCharacters(value) {
  var reg = /^[^\?]+$/;
  if (reg.test(value)) {
    return true;
  }
  else {
    return false;
  }
}
/****************************************To exclude some values from a given RANGE***********************************************/

function excludeFromRange(value) {
  if (value >= 1002 && value <= 1005) {
    return false;
  }
  return true;
}
/***********************************To perform masking for Prefix in Static Routing************************************/
//Determine if string is a valid IP mask; i.e. left contiguous
function isValidSubnetMask(maskStr) {
  if (includeWildIPaddress(maskStr)) {
    if (isDefaultRouting(maskStr)) {
      return true;
    }
    else {
      //var j, str;
      var zeroBit = 0, i, len;
      var foundzero = false;
      // flag - to check its a MASK or not

      var mask = maskStr.split(".");
      // splitted octets with delimiter in ip address

      //var maskInt = [];
      // int octets

      var arr = [];
      // char array of binary string of prefix mask

      var maskBinString;
      //to store the binary concatenated string

      var flag = 0;
      // flag to decide its a mask or not

      var maskBin0 = (parseInt(mask[0], 10)).toString(2);
      //ip address octet values to decimal values to binary values

      var maskBin1 = (parseInt(mask[1], 10)).toString(2);
      var maskBin2 = (parseInt(mask[2], 10)).toString(2);
      var maskBin3 = (parseInt(mask[3], 10)).toString(2);


// append 0's in order to make it 8 bit binary value.
      if ((maskBin0.length) < 8) {
        maskBin0 = zeroBit + maskBin0;

      }
      if ((maskBin1.length) < 8) {
        maskBin1 = zeroBit + maskBin1;

      }
      if ((maskBin2.length) < 8) {
        maskBin2 = zeroBit + maskBin2;

      }
      if ((maskBin3.length) < 8) {
        maskBin3 = zeroBit + maskBin3;

      }

      maskBinString = maskBin0 + maskBin1 + maskBin2 + maskBin3;
      arr = maskBinString.split("");
      len = arr.length;
      switch (len)
      {
        case (8):
          if (maskBinString == "00000000") {
            flag = 0;
          }
          break;

        default:
          for (i = 0; i < len; i++) {
            if (arr[i] == '0') {
            // to check the trail of 1's in the mask value
              foundzero = true;

            }
            else if (arr[i] == '1' && foundzero === true) {

              flag = 0;
              break;

            }
            flag = 1;
          }
          // for loop
          break;
      }
      // switch
      if (flag == 0) {
        return false;
      }
      else {
        return true;
      }
    }
  }
  return false;

}

/**************************To validate Prefix and Prefix Mask together (Prefix & Mask == Prefix)******************************/
function isPrefixAndPrefixMask(maskStr) {
  var prefixStr = $(".isPrefix").val();
  var mask = maskStr.split(".");
  var prefix = prefixStr.split(".");

// all integer values of 4 octets of IPv4

  var mask0 = parseInt(mask[0], 10);
  var prefix0 = parseInt(prefix[0], 10);

  var mask1 = parseInt(mask[1], 10);
  var prefix1 = parseInt(prefix[1], 10);

  var mask2 = parseInt(mask[2], 10);
  var prefix2 = parseInt(prefix[2], 10);

  var mask3 = parseInt(mask[3], 10);
  var prefix3 = parseInt(prefix[3], 10);

  var r0 = prefix0 & mask0;
  var r1 = prefix1 & mask1;
  var r2 = prefix2 & mask2;
  var r3 = prefix3 & mask3;

//validation condition on prefix and prefix mask = Prefix

  if ((r0 == prefix0) && (r1 == prefix1) && (r2 == prefix2) && (r3 == prefix3)) {
    return true;
  }
  else {
    return false;
  }
}
/*********************To validate Prefix and Prefix Mask together for dmvpn (Prefix & Mask == Prefix)*************************/

function isPrefixAndPrefixMaskDmvpn(maskStr) {
  var prefixStr = $(".isPrefixDmvpn").val();
  var mask = maskStr.split(".");
  var prefix = prefixStr.split(".");

// all integer values of 4 octets of IPv4

  var mask0 = parseInt(mask[0], 10);
  var prefix0 = parseInt(prefix[0], 10);

  var mask1 = parseInt(mask[1], 10);
  var prefix1 = parseInt(prefix[1], 10);

  var mask2 = parseInt(mask[2], 10);
  var prefix2 = parseInt(prefix[2], 10);

  var mask3 = parseInt(mask[3], 10);
  var prefix3 = parseInt(prefix[3], 10);

  var r0 = prefix0 & mask0;
  var r1 = prefix1 & mask1;
  var r2 = prefix2 & mask2;
  var r3 = prefix3 & mask3;

//validation condition on prefix and prefix mask = Prefix

  if ((r0 == prefix0) && (r1 == prefix1) && (r2 == prefix2) && (r3 == prefix3)) {
    return true;
  }
  else {
    return false;
  }
}
/************************Automous key validation*****************************/
function isValidAutonomousKey(autonomousKey) {
  var keyRegex = /^\d+$/;
  if (!keyRegex.test(autonomousKey)) {
    return false;
  } else {
    if (autonomousKey > 0 && autonomousKey <= 65535) {
      return true;
    } else {
      return false;
    }
  }
}
/***************************Port validation**************************************************/
function isPortValid(autonomousKey) {
  var reg = /^[a-z|A-Z|0-9]*$/;
  if (autonomousKey > 0 && autonomousKey <= 65535) {
    return true;
  } else if(reg.test(autonomousKey)){
    return true;
  } else {
    return false;
  }
}
/**********************************supporting default static routing*************************************************************/
function isDefaultRouting(maskStr) {
  var prefixStr = $(".isPrefix").val(), reg = /^0.0.0.0$/;


  if (reg.test(maskStr) && reg.test(prefixStr)) {
    return true;
  }
  else {
    return false;
  }
}


/**************************CNS hostname - with two dots and three values, excluding special characters except "-"******************/  function isCNShostname(name) {

  var regAlphaNumHypen = /^[\w\-]+\.[\w\-]+\.[\w\-]+$/,
    regNum = /^[\d]+\.[\d]+\.[\d]+$/;
  if ((regAlphaNumHypen.test(name)) && (!regNum.test(name))) {
    return true;
  }
  return false;
}


/**************************OTASP Phone No. - Number must consist of digits or '*' or '#'******************/
function isOTASPPhoneNo(number) {

  var regNum = /[A-Z| a-z |\^ |\$ |\@ |\! |\( |\) |\% |\& |\? |\< |\> |\- |\/ |\+ | \~]/;
  if (regNum.test(number)) {
    return false;
  }
  return true;
}

/**************************GSM Profile Creation- ? shouldn't be entered******************/
function isAPNUserPswd(value) {

  var regNum = /^\?$/;
  if (regNum.test(value)) {
    return false;
  }
  return true;
}

/****************************HexaKey******************************************************/
function isHexaKeyValue(value) {

  var regNum = /[G-Z| a-z |\^ |\$ |\@ |\! |\( |\) |\% |\& |\? |\< |\> |\- |\/ |\+ | \~]/;
  if (regNum.test(value)) {
    return false;
  }
  return true;
}

function isHexaKeyValueCheck(value) {
  if (value.length == 32 || value.length == 66) {
    return true;
  }
  return false;
}

function isHexaKeyValueLength(value) {
  if (value.length == 32) {
    return true;
  }
  return false;
}

function isHexaKeyValueEncrypt(value) {
  if (value.length == 66) {
    return true;
  }
  return false;
}

function userInputCheck()
{
  var items=[];
    $('#userTable tbody tr td:nth-child(2)').each( function(){
    items.push($(this).text());
    });
    var userInputName = $("#userInput").val();
    var flag = 0;
    for(var i = 0; i < items.length; ++i)
    {
      if(items[i] == userInputName)
      {
        flag = 1;
        break;
      }
    }
    if(flag==1){
      return false;
    }
  else{
    return true;
  }
}

function duplicatePoolCheck()
{
  var items=[];
    $('#dhcpTable tbody tr td:nth-child(2)').each( function(){
    items.push($(this).text());
    });
    var userInputName = $("#poolName").val();
    var flag = 0;
    for(var i = 0; i < items.length; ++i)
    {
      if(items[i] == userInputName)
      {
        flag = 1;
        break;
      }
    }
  if(flag==1){
      return false;
    }
  else{
    return true;
  }
}
/***********************To do Internationalization for validation messages***********************************/
function loadAndDisplayValidationMsgs() {
  languageName();
  /* Validation messages are overidded by properties file in their respective classes. */

  /* Inbuilt validations present in JQuery.validator.js are overriden here*/
  $.validator.messages.required = $.i18n.prop("required");
  $.validator.messages.minlength = $.i18n.prop("minlength");
  $.validator.messages.maxlength = $.i18n.prop("maxlength");
  $.validator.messages.number = $.i18n.prop("number");




}