import './global.js';

Global.Enums.SmsCarriers = {
  ALLTEL: "alltel",
  ATT: "att",
  BOOST_MOBILE: "boost_mobile",
  CRICKET: "cricket",
  SPRINT: "sprint",
  STRAIGHT_TALK: "straight_talk",
  T_MOBILE: "t_mobile",
  TRAC_FONE: "trac_fone",
  US_CELLULAR: "us_cellular",
  VERIZON: "verizon",
  VIRGIN_MOBILE: "virgin_mobile",
  properties: {
    alltel: {name: "Alltel", emailGateway: "sms.alltelwireless.com"},
    att: {name: "AT&T", emailGateway: "txt.att.net"},
    boost_mobile: {name: "Boost Mobile", emailGateway: "myboostmobile.com"},
    cricket: {name: "Cricket", emailGateway: "sms.mycricket.com"},
    sprint: {name: "Sprint", emailGateway: "messaging.sprintpcs.com"},
    straight_talk: {name: "Straight Talk", emailGateway: "vtext.com"},
    t_mobile: {name: "T-Mobile", emailGateway: "tmomail.net"},
    trac_fone: {name: "TracFone", emailGateway: "mmst5.tracfone.com"},
    us_cellular: {name: "US Cellular", emailGateway: "email.uscc.com"},
    verizon: {name: "Verizon", emailGateway: "vtext.com"},
    virgin_mobile: {name: "Virgin Mobile", emailGateway: "vmobl.com"}
  },
  enumCount() {
    // Filter out the non-enum keys before taking length.
    return Object.keys(this).filter(key => typeof this[key] === "string").length;
  },
  getName(enumeration) {
    for (let key of this.listEnumKeys()) {
      if (this[key] === enumeration) {
        return this.properties[enumeration].name;
      }
    }
  },
  listEnumKeys() {
    // Filter out the non-enum object keys.
    return Object.keys(this).filter(key => typeof this[key] === "string");
  },
  listEnumValues() {
    return this.listEnumKeys().map(key => this[key]);
  },
  getEnumKeyByName(name) {
    for (let propertyKey in this.properties) {
      if (this.properties[propertyKey].name === name) {
        return Object.keys(this).find(key => this[key] == propertyKey);
      }
    }
    return undefined;
  },
  listOfCarrierNames() {
    // Filter out the non-enum object keys.
    return Object.keys(this.properties).map(key => this.properties[key].name);
  },
  getEmailGateway(enumeration) {
    for (let key of this.listEnumKeys()) {
      if (this[key] === enumeration) {
        return this.properties[enumeration].emailGateway;
      }
    }
  }
};


// AKA PacketType from OPQ Protocol.
Global.Enums.EventTypes = {
  EVENT_HEARTBEAT: 0,
  EVENT_FREQUENCY: 1,
  EVENT_VOLTAGE: 2,
  EVENT_DEVICE: 3,
  properties: {
    0: {name: "Heartbeat Event"},
    1: {name: "Frequency Event"},
    2: {name: "Voltage Event"},
    3: {name: "Device Event"}
  },
  enumCount() {
    // Filter out the non-enum keys before taking length.
    return Object.keys(this).filter(key => typeof this[key] === "number").length;
  },
  getName(enumeration) {
    for (let key of this.listEnumKeys()) {
      if (this[key] === enumeration) {
        return this.properties[enumeration].name;
      }
    }
  },
  listEnumKeys() {
    // Filter out the non-enum object keys.
    return Object.keys(this).filter(key => typeof this[key] === "number");
  },
  listEnumValues() {
    return this.listEnumKeys().map(key => this[key]);
  },
  getEnumKeyByName(name) {
    for (let propertyKey in this.properties) {
      if (this.properties[propertyKey].name === name) {
        return Object.keys(this).find(key => this[key] == propertyKey);
      }
    }
    return undefined;
  },
  listOfEventTypeNames() {
    // Filter out the non-enum object keys.
    return Object.keys(this.properties).map(key => this.properties[key].name);
  }
};


Global.Enums.IticRegion = { // Rethink this one.
  NO_INTERRUPTION: 0,
  NO_DAMAGE: 1,
  PROHIBITED: 2,
  UNKNOWN: 3,
  properties: {
    0: {name: "No Interruption", severity: 2, severityName: "Ok"},
    1: {name: "No Damage", severity: 1, severityName: "Moderate"},
    2: {name: "Prohibited", severity: 0, severityName: "Severe"},
    3: {name: "Unknown", severity: -1, severityName: "Unknown"}
  },
  enumCount() {
    // Filter out the non-enum keys before taking length.
    return Object.keys(this).filter(key => typeof this[key] === "number").length;
  },
  getName(enumeration) {
    for (let key of this.listEnumKeys()) {
      if (this[key] === enumeration) {
        return this.properties[enumeration].name;
      }
    }
  },
  listEnumKeys() {
    // Filter out the non-enum object keys.
    return Object.keys(this).filter(key => typeof this[key] === "number");
  },
  listEnumValues() {
    return this.listEnumKeys().map(key => this[key]);
  },
  getEnumKeyByName(name) {
    for (let propertyKey in this.properties) {
      if (this.properties[propertyKey].name === name) {
        return Object.keys(this).find(key => this[key] == propertyKey);
      }
    }
    return undefined;
  },
  listOfIticRegionNames() {
    // Filter out the non-enum object keys.
    return Object.keys(this.properties).map(key => this.properties[key].name);
  }
};

//console.log(Global.Enums.SmsCarriers.listEnumKeys());
//console.log(Global.Enums.SmsCarriers.listEnumValues());
//console.log(Global.Enums.SmsCarriers.getName(Global.Enums.SmsCarriers.BOOST_MOBILE))
//console.log(Global.Enums.SmsCarriers.getEmailGateway(Global.Enums.SmsCarriers.BOOST_MOBILE));
//console.log(Global.Enums.SmsCarriers.getEnumKeyByName("AT&T"));
//console.log(Global.Enums.SmsCarriers.listOfCarrierNames());