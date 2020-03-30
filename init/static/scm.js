function add_product_to_order()
{
    var products_list = document.getElementsByName("product[]")
    var len = products_list.length

    var last_product = products_list[len - 1]
    last_product.id = "product_" + (len-1).toString()
    var next_product = last_product.cloneNode(true)
    next_product.id = "product_" + len.toString()

    var product_label = next_product.children[1].children[0]
    product_label.innerHTML = `Details on product ${(len + 1).toString()}:`

    var taste_choices = next_product.children[2].children[1]
    var decoration_form_choices = next_product.children[3].children[1]    
    var decoration_technique_choices = next_product.children[4].children[1]
    var delete_btn = next_product.children[5].children[0]

    taste_choices.id = "taste_choices_" + len.toString()
    decoration_form_choices.id = "decoration_form_choices_" + len.toString()
    decoration_technique_choices.id = "decoration_technique_choices_" + len.toString()
    delete_btn.id = "delete_product_" + len.toString()

    taste_choices.name = "taste_choices_" + len.toString()
    decoration_form_choices.name = "decoration_form_choices_" + len.toString()
    decoration_technique_choices.name = "decoration_technique_choices_" + len.toString()

    last_product.insertAdjacentElement("afterend", next_product)
    return false;
}

function delete_product(control)
{
    var products_list = document.getElementsByName("product[]")
    var len = products_list.length
    if (len > 1)
    {
        var strIndex = get_index(control)
        var intIndex = parseInt(strIndex)
        document.getElementById("product_" + strIndex).remove()
        products_list = document.getElementsByName("product[]")

        for (var i = intIndex; i < products_list.length; i++)
        {
	        product = products_list[i]
	        product.id = "product_" + i.toString()
    
            var product_label = product.children[1].children[0]
            product_label.innerHTML = `Details on product ${(i+1).toString()}:`

            var taste_choices = product.children[2].children[1]
            var decoration_form_choices = product.children[3].children[1]    
            var decoration_technique_choices = product.children[4].children[1]
            var delete_btn = product.children[5].children[0]

	        taste_choices.id = "taste_choices_" + i.toString()
	        decoration_form_choices.id = "decoration_form_choices_" + i.toString()
	        decoration_technique_choices.id = "decoration_technique_choices_" + i.toString()
	        delete_btn.id = "delete_product_" + i.toString()

	        taste_choices.name = "taste_choices_" + i.toString()
	        decoration_form_choices.name = "decoration_form_choices_" + i.toString()
            decoration_technique_choices.name = "decoration_technique_choices_" + i.toString()
        }
    }
    else
    {
        window.alert('Cannot delete this only product!')
    }
}

function add_another_material()
{
    var materials_list = document.getElementsByName("material[]")
    var len = materials_list.length
  
    var last_material = materials_list[len - 1]
    last_material.id = "material_" + (len-1).toString()
    var next_material = last_material.cloneNode(true)
    next_material.id = "material_" + len.toString()

    var material_choices = next_material.children[0]
    var material_amount = next_material.children[1]
    var material_unit_price = next_material.children[2]
    var material_cost = next_material.children[3]
    var delete_btn = next_material.children[4]

    material_choices.id = "material_choices_" + len.toString()
    material_amount.id = "material_amount_" + len.toString()
    material_unit_price.id = "material_unit_price_" + len.toString()
    material_cost.id = "material_cost_" + len.toString()
    delete_btn.id = "delete_material_" + len.toString()

    material_choices.name = "material_choices_" + len.toString()
    material_amount.name = "material_amount_" + len.toString()
    material_unit_price.name = "material_unit_price_" + len.toString()
    material_cost.name = "material_cost_" + len.toString()

    for (var i = 0; i < material_choices.options.length; i++)
    {
	material_choices.options[i].selected = false
    }
    
    material_choices.options[0].selected = true
    material_amount.value = ""
    material_unit_price.selectedIndex = 0
    material_cost.value = ""
  
    last_material.insertAdjacentElement("afterend", next_material)
    return false;
}

function get_index(control)
{
    var my_name = control.id
    var pos = my_name.lastIndexOf("_")
    return my_name.substring(pos+1)
}

function delete_material(control)
{
    var materials_list = document.getElementsByName("material[]")
    var len = materials_list.length

    if (len > 1)
    {
        var strIndex = get_index(control)
        var intIndex = parseInt(strIndex)
        document.getElementById("material_" + strIndex).remove()

        materials_list = document.getElementsByName("material[]")

        for (var i = intIndex; i < materials_list.length; i++)
        {
            material = materials_list[i]
            material.id = "material_" + i.toString()
            
            var material_choices = material.children[0]
            var material_amount = material.children[1]
            var material_unit_price = material.children[2]
            var material_cost = material.children[3]
            var delete_btn = material.children[4]

            material_choices.id = "material_choices_" + i.toString()
            material_amount.id = "material_amount_" + i.toString()
            material_unit_price.id = "material_unit_price_" + i.toString()
            material_cost.id = "material_cost_" + i.toString()
            delete_btn.id = "delete_material_" + i.toString()

            material_choices.name = "material_choices_" + i.toString()
            material_amount.name = "material_amount_" + i.toString()
            material_unit_price.name = "material_unit_price_" + i.toString()
            material_cost.name = "material_cost_" + i.toString()
        }
    }
    else
    {
        window.alert('Cannot delete this only material!')
    }
}

function sync_unit_price(control)
{
    var strIndex = get_index(control)
    
    var my_material_amount_id = "material_amount_" + strIndex  
    var my_material_unit_price_id = "material_unit_price_" + strIndex
    var my_material_cost_id = "material_cost_" + strIndex

    var my_material_unit_price = document.getElementById(my_material_unit_price_id)
    my_material_unit_price.selectedIndex = control.selectedIndex
}

function update_cost(control)
{
    var strIndex = get_index(control)
    
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

sComboBoxChangeOneLevel = function(element) {
    $(element).select2();
    jQuery(element).change(function() {
	let currentHref = location.href;

	let currentHrefComponents = currentHref.split("/");
	let parentHref = currentHrefComponents.slice(0, currentHrefComponents.length-1).join("/");

	let chosen_item = jQuery(this).val();
	location.href = parentHref + "/" + chosen_item
    })
};
