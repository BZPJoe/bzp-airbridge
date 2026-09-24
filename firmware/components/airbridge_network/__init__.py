import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID
from esphome import pins

DEPENDENCIES = ["wifi", "web_server"]
ns = cg.esphome_ns.namespace("airbridge_network")
Network = ns.class_("Network", cg.Component)
CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(Network),
    cv.Required("pairing_key"): cv.string,
    cv.Required("pairing_pin"): pins.gpio_input_pin_schema,
}).extend(cv.COMPONENT_SCHEMA)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    cg.add(var.set_pairing_key(config["pairing_key"]))
    cg.add(var.set_pairing_pin(await cg.gpio_pin_expression(config["pairing_pin"])))
