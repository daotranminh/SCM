function validate_add_order()
{
    var products_list = document.getElementsByName("product[]")

    for (var i=0; i < products_list.length; ++i)
    {
        var product_name = products_list[i].children[2].children[1].value
        var product_amount = products_list[i].children[3].children[1].value
        var taste_choice = products_list[i].children[4].children[1].value
        var formula_choice = products_list[i].children[5].children[1].value
        var decoration_form_choices = products_list[i].children[6].children[1].value 
        var decoration_technique_choices = products_list[i].children[7].children[1].value        

        if (product_name == "")
        {
            alert("Please enter a product name for product " + (i+1).toString() + "!")
            return false
        }

        if (taste_choice == "-1")
        {
            alert("Please choose a taste for product " + (i+1).toString() + "!")
            return false
        }

        if (formula_choice == "-1" || formula_choice == "")
        {
            alert("Please choose a formula for product " + (i+1).toString() + "!")
            return false
        }
    }
}

function update_total_price_to_customer(control)
{
    var totalProductPriceToCustomer = 0
    var productPrices = document.querySelectorAll('*[id^="price_to_customer_"]')
    for (var i=0; i < productPrices.length; i++)
    {
        var productPrice = parseFloat(productPrices[i].value)
        if (isNaN(productPrice) == false)
        {
            totalProductPriceToCustomer += productPrice
        }
    }

    var totalProductPriceToCustomerTxt = document.getElementById("total_price_to_customer")
    totalProductPriceToCustomerTxt.value = totalProductPriceToCustomer
}

function extract_update_order_args()
{
    var customerId = document.getElementById("customer_id").value
    var orderedOn = document.getElementById("ordered_on").value
    var deliveryAppointment = document.getElementById("delivery_appointment").value
    var deliveryMethodId = document.getElementById("delivery_method_id").value
    var orderStatus = document.getElementById("order_status").value
    var deliveredOn = document.getElementById("delivered_on").value
    var paymentStatus = document.getElementById("payment_status").value
    var paidOn = document.getElementById("paid_on").value
    var message = document.getElementById("message").value

    var newProductName = document.getElementById("new_product_name").value
    var product_amount = document.getElementById("product_amount").value
    var tasteId = document.getElementById("taste_id").value
    var formulaId = document.getElementById("formula_id").value
    var decorationFormId = document.getElementById("decoration_form_id").value
    var decorationTechniqueId = document.getElementById("decoration_technique_id").value
    var withBox = document.getElementById("with_box").checked

    var existingProductIds = document.querySelectorAll('*[id^="product_id_"]');
    var existingProductPriceIds = document.querySelectorAll('*[id^="price_to_customer_"]');
	var priceToCustomersStr = ""
	for (var i=0; i < existingProductIds.length; i++)
	{
		var productId = existingProductIds[i].innerText
		var productPrice = existingProductPriceIds[i].value
		priceToCustomersStr = priceToCustomersStr + productId + "--" + productPrice + "!!!!"
    }
    
    return [customerId,             // 0
            orderedOn,              // 1
            deliveryAppointment,    // 2
            deliveryMethodId,       // 3
            orderStatus,            // 4
            deliveredOn,            // 5
            paymentStatus,          // 6
            paidOn,                 // 7
            message,                // 8
            newProductName,         // 9
            product_amount,         // 10
            tasteId,                // 11
            formulaId,              // 12
            decorationFormId,       // 13
            decorationTechniqueId,  // 14
            withBox,                // 15
            priceToCustomersStr]    // 16
}

function delete_product_in_update_order(delete_btn)
{
    if (confirm('Are you sure to delete this product?') == false)
    {
        return;
    }

    var count = $('#existing_products_table tr').length;

    if (count == 3)
    {
        window.alert('Cannot delete this only product!')
        return;
    }

    var productId = get_index(delete_btn)

    var args = extract_update_order_args()
    var customerId = args[0]
    var orderedOn = args[1]
    var deliveryAppointment = args[2]
    var deliveryMethodId = args[3]
    var orderStatus = args[4]
    var deliveredOn = args[5]
    var paymentStatus = args[6]
    var paidOn = args[7]
    var message = args[8]
    var newProductName = args[9]
    var product_amount = args[10]
    var tasteId = args[11]
    var formulaId = args[12]
    var decorationFormId = args[13]
    var decorationTechniqueId = args[14]
    var withBox = args[15]
    var priceToCustomersStr = args[16]

    currentHref = location.href
    currentHrefComponents = currentHref.split("/")
    baseHref = currentHrefComponents.slice(0,3).join("/")
    newHref = baseHref + "/delete_product/" + productId + 
        "?customer_id_arg=" + customerId +
        "&ordered_on_arg=" + orderedOn +
        "&delivery_appointment_arg=" + deliveryAppointment +
        "&delivery_method_id_arg=" + deliveryMethodId +
        "&order_status_arg=" + orderStatus +
        "&delivered_on_arg=" + deliveredOn +
        "&payment_status_arg=" + paymentStatus +
        "&paid_on_arg=" + paidOn +
        "&message_arg=" + message +
        "&new_product_name_arg=" + newProductName +
        "&product_amount_arg=" + product_amount +
        "&taste_id_arg=" + tasteId +
        "&formula_id_arg=" + formulaId +
        "&decoration_form_id_arg=" + decorationFormId +
        "&decoration_technique_id_arg=" + decorationTechniqueId +
        "&with_box_arg=" + withBox +
        "&price_to_customers_arg=" + priceToCustomersStr
        
    location.href = newHref
}

function update_order_taste_change(taste_choices)
{
    var formula_choices = document.getElementById("formula_id")

    while (formula_choices.options.length > 0)
    {
        formula_choices.remove(0)
    }

    var taste_choice_id = parseInt(taste_choices.value)
    if (taste_choice_id != -1)
    {
        formula_ids = taste_formula_dict[taste_choice_id]
        for (let i = 0; i < formula_ids.length; ++i)
        {
            var opt = document.createElement("option")
            opt.value = formula_ids[i]
            opt.innerHTML = formula_dict[formula_ids[i]]
            formula_choices.appendChild(opt)
        }
    }
}

function taste_change(taste_choices)
{
    var strIndex = get_index(taste_choices)
    var formula_choices_id = "formula_choices_" + strIndex
    var formula_choices = document.getElementById(formula_choices_id)

    while (formula_choices.options.length > 0)
    {
        formula_choices.remove(0)
    }

    var taste_choice_id = parseInt(taste_choices.value)
    if (taste_choice_id != -1)
    {
        formula_ids = taste_formula_dict[taste_choice_id]
        for (let i = 0; i < formula_ids.length; ++i)
        {
            var opt = document.createElement("option")
            opt.value = formula_ids[i]
            opt.innerHTML = formula_dict[formula_ids[i]]
            formula_choices.appendChild(opt)
        }
    }
}

function add_new_product_to_order()
{
    var orderId = document.getElementById("order_id").value

    var args = extract_update_order_args()
    var customerId = args[0]
    var orderedOn = args[1]
    var deliveryAppointment = args[2]
    var deliveryMethodId = args[3]
    var orderStatus = args[4]
    var deliveredOn = args[5]
    var paymentStatus = args[6]
    var paidOn = args[7]
    var message = args[8]
    var newProductName = args[9]
    var product_amount = args[10]
    var tasteId = args[11]
    var formulaId = args[12]
    var decorationFormId = args[13]
    var decorationTechniqueId = args[14]
    var withBox = args[15]
    var priceToCustomersStr = args[16]

    if (newProductName == "")
    {
        alert("Please enter product's name!")
        return false;
    }

    if (tasteId == "-1")
    {
        alert("Please choose a taste!")
        return false;
    }

    currentHref = location.href
	currentHrefComponents = currentHref.split("/")
    baseHref = currentHrefComponents.slice(0,3).join("/")
    newHref = baseHref + "/add_new_product_to_order/" + orderId + 
        "?customer_id_arg=" + customerId +
        "&ordered_on_arg=" + orderedOn +
        "&delivery_appointment_arg=" + deliveryAppointment +
        "&delivery_method_id_arg=" + deliveryMethodId +
        "&order_status_arg=" + orderStatus +
        "&delivered_on_arg=" + deliveredOn +
        "&payment_status_arg=" + paymentStatus +
        "&paid_on_arg=" + paidOn +
        "&message_arg=" + message +
        "&new_product_name_arg=" + newProductName +
        "&product_amount_arg=" + product_amount +
        "&taste_id_arg=" + tasteId +
        "&formula_id_arg=" + formulaId +
        "&decoration_form_id_arg=" + decorationFormId +
        "&decoration_technique_id_arg=" + decorationTechniqueId +
        "&with_box_arg=" + withBox +
        "&price_to_customers_arg=" + priceToCustomersStr
    
    location.href = newHref
}


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

    var product_name = next_product.children[2].children[1]
    var product_amount = next_product.children[3].children[1]
    var taste_choices = next_product.children[4].children[1]
    var formula_choices = next_product.children[5].children[1]
    var decoration_form_choices = next_product.children[6].children[1]    
    var decoration_technique_choices = next_product.children[7].children[1]
    var delete_btn = next_product.children[8].children[0]

    product_name.id = "product_name_" + len.toString()
    product_name.value = ""
    product_amount.id = "product_amount_" + len.toString()
    product_amount.value = "1"
    taste_choices.id = "taste_choices_" + len.toString()
    formula_choices.id = "formula_choices_" + len.toString()
    decoration_form_choices.id = "decoration_form_choices_" + len.toString()
    decoration_technique_choices.id = "decoration_technique_choices_" + len.toString()
    delete_btn.id = "delete_product_" + len.toString()

    product_name.name = "product_name_" + len.toString()
    product_amount.name = "product_amount_" + len.toString()
    taste_choices.name = "taste_choices_" + len.toString()
    formula_choices.name = "formula_choices_" + len.toString()
    decoration_form_choices.name = "decoration_form_choices_" + len.toString()
    decoration_technique_choices.name = "decoration_technique_choices_" + len.toString()

    last_product.insertAdjacentElement("afterend", next_product)
    return false;
}

function delete_product(control)
{
    if (confirm('Are you sure to delete this product?') == false)
    {
        return;
    }

    var products_list = document.getElementsByName("product[]")
    var len = products_list.length

    if (len <= 1)
    {
        window.alert('Cannot delete this only product!')
        return;
    }

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

        var product_name = product.children[2].children[1]
        var product_amount = product.children[3].children[1]
        var taste_choices = product.children[4].children[1]
        var formula_choices = product.children[5].children[1]
        var decoration_form_choices = product.children[6].children[1]    
        var decoration_technique_choices = product.children[7].children[1]
        var delete_btn = product.children[8].children[0]

        product_name.id = "product_name_" + i.toString()
        product_amount.id = "product_amount_" + i.toString()
        taste_choices.id = "taste_choices_" + i.toString()
        formula_choices.id = "formula_choices_" + i.toString()
	    decoration_form_choices.id = "decoration_form_choices_" + i.toString()
	    decoration_technique_choices.id = "decoration_technique_choices_" + i.toString()
	    delete_btn.id = "delete_product_" + i.toString()

        product_name.name = "product_name_" + i.toString()
	    taste_choices.name = "taste_choices_" + i.toString()
	    decoration_form_choices.name = "decoration_form_choices_" + i.toString()
        decoration_technique_choices.name = "decoration_technique_choices_" + i.toString()
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

function __update_cost(strIndex)
{
    var my_material_amount_id = "material_amount_" + strIndex  
    var my_material_unit_price_id = "material_unit_price_" + strIndex
    var my_material_cost_id = "material_cost_" + strIndex

    var my_material_amount = document.getElementById(my_material_amount_id)
    var my_material_unit_price = document.getElementById(my_material_unit_price_id)
    var my_material_cost = document.getElementById(my_material_cost_id)

    var amount = parseFloat(my_material_amount.value)
    var unit_price = parseFloat(my_material_unit_price.value)
    my_material_cost.value = amount * unit_price

    var materials_list = document.getElementsByName("material[]")
    var len = materials_list.length
    var total_cost = 0
    
    for (var i = 0; i < len; i++) 
    {
	    var material_cost_id = "material_cost_" + i.toString()
	    var material_cost = document.getElementById(material_cost_id)
	    var cost = parseFloat(material_cost.value)
	    total_cost += cost
    }

    var txt_total_cost = document.getElementById("total_cost")
    txt_total_cost.value = total_cost
}

function sync_unit_price(control)
{
    var strIndex = get_index(control)
    var my_material_unit_price = document.getElementById("material_unit_price_" + strIndex)
    my_material_unit_price.selectedIndex = control.selectedIndex
    
    __update_cost(strIndex)
}

function update_cost(control)
{
    var strIndex = get_index(control)
    
    __update_cost(strIndex)

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

sComboBoxChangeFirstLevel = function(element) {
    $(element).select2();
    jQuery(element).change(function() {
	let currentHref = location.href;

    let currentHrefComponents = currentHref.split("/");
    currentHrefComponents[4] = this.value
    let newHref = currentHrefComponents.join("/");
    
	location.href = newHref
    })
};
