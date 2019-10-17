function add_another_material()
{
    var materials_list = document.getElementsByName("material[]")
    var len = materials_list.length
  
    var last_material = materials_list[len - 1]
    var next_material = last_material.cloneNode(true)

    var material_choices = next_material.children[0]
    var material_amount = next_material.children[1]
    var material_unit_price = next_material.children[2]
    var material_cost = next_material.children[3]

    material_choices.id = "material_choices_" + len.toString()
    material_amount.id = "material_amount_" + len.toString()
    material_unit_price.id = "material_unit_price_" + len.toString()
    material_cost.id = "material_cost_" + len.toString()

    material_choices.name = "material_choices_" + len.toString()
    material_amount.name = "material_amount_" + len.toString()
    material_unit_price.name = "material_unit_price_" + len.toString()
    material_cost.name = "material_cost_" + len.toString()
  
    material_choices.seletedIndex = 0
    material_amount.value = ""
    material_unit_price.selectedIndex = 0
    material_cost.value = ""
  
    last_material.insertAdjacentElement("afterend", next_material)
    return false;
}

function sync_unit_price(control)
{
    var my_name = control.id
    var pos = my_name.lastIndexOf("_")
    var strIndex = my_name.substring(pos+1)

    var my_material_amount_id = "material_amount_" + strIndex  
    var my_material_unit_price_id = "material_unit_price_" + strIndex
    var my_material_cost_id = "material_cost_" + strIndex

    var my_material_unit_price = document.getElementById(my_material_unit_price_id)
    my_material_unit_price.selectedIndex = control.selectedIndex
}

function update_cost(control)
{
    var my_name = control.id
    var pos = my_name.lastIndexOf("_")
    var strIndex = my_name.substring(pos+1)
    
    var my_material_unit_price_id = "material_unit_price_" + strIndex
    var my_material_cost_id = "material_cost_" + strIndex

    var my_material_unit_price = document.getElementById(my_material_unit_price_id)
    var my_material_cost = document.getElementById(my_material_cost_id)
    
    var unit_price = parseFloat(my_material_unit_price.value)
    var amount = parseFloat(control.value)
    var cost = amount * unit_price
    my_material_cost.value = cost
    
    var materials_list = document.getElementsByName("material[]")
    var len = materials_list.length
    var total_cost = 0
    
    for (var i = 0; i < len; i++) {
	var material_cost_id = "material_cost_" + i.toString()
	var material_cost = document.getElementById(material_cost_id)
	var cost = parseFloat(material_cost.value)
	total_cost += cost
    }

    var txt_total_cost = document.getElementById("total_cost")
    txt_total_cost.value = total_cost
    
    
    return false;
}
