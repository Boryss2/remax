console.log("working fine");

const monthNames = ["Jan", "Feb", "Mar", "April", "May", "June",
  "July", "Aug", "Sept", "Oct", "Nov", "Dec"
];

    // Add to cart functionality
    $(".add-to-cart-btn").on("click", function () {
        let this_val = $(this);
        let index = this_val.attr("data-index");

        let quantity = $(".product-quantity-" + index).val();
        let product_title = $(".product-title-" + index).val();
        let product_id = $(".product-id-" + index).val();
        let product_price = $(".current-product-price-" + index).text();
        let product_pid = $(".product-pid-" + index).val();
        let product_image = $(".product-image-" + index).val();

        let variant_id = $("#variant-selector").val();

        console.log("Quantity:", quantity);
        console.log("Title:", product_title);
        console.log("Price:", product_price);
        console.log("ID:", product_id);
        console.log("PID:", product_pid);
        console.log("Image:", product_image);
        console.log("Index:", index);
        console.log("Currrent Element:", this_val);
        console.log("Variant ID:", variant_id);

        $.ajax({
            url: '/add-to-cart',
            data: {
                'id': product_id,
                'pid': product_pid,
                'image': product_image,
                'qty': quantity,
                'title': product_title,
                'price': product_price,
                'variant_id': variant_id,  // Include variant ID in the request
            },
            dataType: 'json',
            beforeSend: function () {
                console.log("Adding Product to Cart...");
            },
            success: function (response) {
                // this_val.html("✓")
                this_val.html("<i class='fas fa-check-circle'></i>");

                console.log("Added Product to Cart!");
                $(".cart-items-count").text(response.totalcartitems);
            }
        });
    });



    //UPDATE CART
    $(document).on('submit', 'form.update-product', function(event) {
        event.preventDefault();
    
        var form = $(this);
        var url = form.attr('action');
        var data = form.serialize();
    
        $.post(url, data, function(response) {
            // Handle the response, e.g., update the displayed cart information
            console.log(response);
        });
    });


    //DELETE ITEM FROM CART
    $(document).on('submit', 'form.delete-item-form', function(event) {
        event.preventDefault();
    
        var form = $(this);
        var url = form.attr('action');
        var productId = form.find('[name="product_id"]').val(); // Get the product_id from the form
        var csrfToken = form.find('[name="csrfmiddlewaretoken"]').val(); // Get the CSRF token
    
        $.ajax({
            type: 'POST',
            url: url,
            data: { product_id: productId },
            headers: {
                'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
            },
            success: function(response) {
                console.log(response);
    
                if (response.message === 'Success') {
                    console.log("Product removed successfully");
                    // Refresh the page to update the cart
                    location.reload();
                } else {
                    console.error("Error removing product:", response.message);
                }
            },
            error: function(response) {
                console.error("Error:", response);
            }
        });
    });

    // MAKING DEFAULT ADDRESS
    $(document).on("click", ".make-default-address", function(){
        let id = $(this).attr("data-address-id")
        let this_val = $(this)

        console.log("ID is:", id);
        console.log("Element is:", this_val);

        $.ajax({
            url: "/make-default-address",
            data: {
                "id":id
            },
            dataType: "json",
            success: function(response){
                console.log("Address Made Default....");
                if (response.boolean == true){

                    $(".check").hide()
                    $(".action_btn").show()

                    $(".check"+id).show()
                    $(".button"+id).hide()
                    location.reload();
                }
            }
        })
    })
