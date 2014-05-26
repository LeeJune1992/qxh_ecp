//var Core = {
//    init: function() {
//
//
//        Core.multiple_change_checked('#content .ids-control', '#content .ids');
//    },
//
//    multiple_change_checked: function(control, group) {
//        $(control).bind('change', function() {
//            if ($(this).is(':checked')) {
//                $(group).attr('checked', 'checked');
//            } else {
//                $(group).removeAttr('checked', 'checked');
//            }
//        });
//    }
//};

var escape_html = function(html){
    return html.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\/g,'&#92;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/\n/g,'');
};


var hide_phone = function(phone){
    if (phone != '' && phone != null && phone.length>=7){
    var p =phone.substr(3,4);
    return phone.replace(p,'****');
    }
    return '';
}

var validate_phone = function(phone){
    //return true;
//    var reg = /^(1[3|5|8])[\d]{9}$/;
//    if(!reg.test(phone)){
//        return false;
//    }
//    return true;

    var pattern=/(^[2-9]{1}[0-9]{7}$)|(^(0)[2-9]{1}[0-9]{8,10}$)|(^(010)[2-9]{1}[0-9]{7}$)|(^(1[3|4|5|6|8])[\d]{9}$)/;
    //var pattern=/(^[0-9]{3,4}\-[0-9]{3,8}$)|(^[0-9]{8,12}$)|(^\([0-9]{3,4}\)[0-9]{3,8}$)|(^(1[3|4|5|6|8])[\d]{9}$)/;
    if(pattern.test(phone))
    {
        return true;
    }
    else
    {
        return false;
    }
};
var validate_zip = function(phone){
    var pattern=/^[0-9]\d{5}$/;
    if(pattern.test(phone))
    {
        return true;
    }
    else
    {
        return false;
    }
};

var address = {
    reset:function(){
        $('#ship_to').val(null);
        $('#province').val(null).change();
        $('#city').val(null).change();
        $('#district').val(null).change();
        $('#street1').val(null);
        $('#phone').val(null);
        $('#tel').val(null);
        $('#email').val(null);
        $('#postcode').val(null);
        $('#address_id').val(0);
        $('#update_address').hide();
    },
    cleanup:function(){
        address.reset();
        $('#address_list').hide();
    },
    show: function (user_id) {
        if (isNaN(user_id) || user_id == 0) {
            $('#address_list').hide();
            return false;
        }
        $('#address_list').show();
        $.ajax({
            url: "/api/address/" + user_id,
            dataType: "json",
            cache:false,
            type: 'GET'
        }).done(function (data) {
                var list = $("#address_list ul");
                //var template = '<li><input id="addr-$aid" name="old_address" type="radio" value="$aid" $attrs /><label for="addr-$aid"><span style="color:blue">$ship_to</span> $address $phone</label></li>';
                list.empty();
                $.each(data.addresses, function () {
                    var attrs = '';
                    $.each(this, function (i, item) {
                        attrs += i + '="' + item + '" ';
                    });

                    var opt = '<li><input id="addr-'+this.id+'" name="old_address" type="radio" value="'+this.id+'" '+attrs+' /><label for="addr-'+this.id+'"><span style="color:blue">'+this.ship_to+'</span> '+this.format_address+' '+this.phone+' </label></li>';
                    list.append(opt);
//                    var markup = template
//                        .replace(/\$aid/g, this.id)
//                        .replace(/\$ship_to/g, this.ship_to)
//                        .replace(/\$phone/g, this.phone)
//                        .replace(/\$attrs/g, attrs)
//                        .replace(/\$address/g, this.format_address);
                    //list.append(markup);
                });

                var address_id = parseInt($('#address_id').val());
                if(address_id>0){
                    $('#addr-'+address_id).attr('checked','checked');
                }

                $('input[name=old_address]').change(function () {
                    var $selected = $("input[name=old_address]:checked");
                    if ($selected != null) {
                        $('#update_address').show();
                        $('#address_id').val($selected.val());
                        $.each(['ship_to', 'street1', 'postcode', 'phone', 'tel', 'email'], function (k, i) {
                            $('#' + i).val($selected.attr(i));
                        });

                        $.each(['province', 'city', 'district'], function (k, i) {
                            $('#' + i).val($selected.attr(i)).change();
                        });
                        $('#reset_address').show();
                    }
                    else{
                        $('#reset_address').hide();
                    }
                });

            }).fail(function () {
                $("#address_list ul").empty().append("<li class='alert alert-error'>未添加地址</li>");
            });
    },
    update: function (callback_func) {
        var user_id = parseInt($('#user_id').val());
        if (isNaN(user_id) || user_id == 0) {
            bootbox.alert('无法更新收货地址');
            return false;
        }
        var address_id = parseInt($('#address_id').val());
        if (isNaN(address_id)) {
            address_id = 0;
        }

        var province = $('#province').val();
        if (province == ''){
            bootbox.alert('请选择省份！');
            return false;
        }

        var ship_to = $('#ship_to').val();
        if (!ship_to) {
            bootbox.alert('收货人姓名不能为空');
            return false;
        }
        var street = $('#street1').val();
        if (!street) {
            bootbox.alert('地址不能为空');
            return false;
        }

        var phone = $('#phone').val();
        if (!validate_phone(phone)) {
            bootbox.alert('电话号码输入不正确。本地座机号码不加区号028，手机号首位请勿为0。',function(){
                $('#phone').focus();
            });
            return false;
        }

        var tel = $('#tel').val();
        if(tel != '' && !validate_phone(tel)){
            bootbox.alert('电话号码输入不正确。本地座机号码不加区号028，手机号首位请勿为0。',function(){
                $('#tel').focus();
            });
            return false;
        }

        var url = "/address/update/" + address_id +'/' + user_id;
        var req = $.ajax({
            url: url,
            dataType: 'json',
            type: 'POST',
            data: {
                ship_to: ship_to,
                province: province,
                city: $('#city').val(),
                district: $('#district').val(),
                street1: street,
                phone: phone,
                tel: $('#tel').val(),
                email: $('#email').val(),
                postcode: $('#postcode').val()
            }
        });

        req.done(function(data) {
            if (callback_func){
                callback_func(data);
            }
            else{
                var $result = $('#update_address span');
                if (data.result == true) {

                    $result.css('color', 'green');
                    $result.empty().html('地址更新成功');
                    address.show(parseInt($('#user_id').val()));
                }
                else {
                    $result.css('color', 'red');
                    $result.empty().html('地址更新失败:' + data.error);
                }
            }
        });

        req.fail(function(request, status, error) {
            bootbox.alert('地址更新失败:' + error);
        });
    }
};



$(document).ready( function() {
    //Core.init();
//    var elements = document.getElementsByTagName("input");
//    for (var i = 0; i < elements.length; i++) {
//        elements[i].oninvalid = function(e) {
//            e.target.setCustomValidity("");
//            if (!e.target.validity.valid) {
//                e.target.setCustomValidity("该项不可为空");
//            }
//        };
//    }
    $('#datepicker').datepicker({
        format: 'yyyy-mm-dd',
        language: 'zh-CN'});

    $('input, textarea').placeholder();

    $('a.back').on('click',function(){
        parent.history.back();
        //window.location.replace(document.referrer);
        return false;
    });

//    $('a[data-confirm]').click(function(ev) {
//        var href = $(this).attr('href');
//
//        if (!$('#dataConfirmModal').length) {
//            $('body').append('<div id="dataConfirmModal" class="modal fade" role="dialog" aria-labelledby="dataConfirmLabel" aria-hidden="true"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button><h3 id="dataConfirmLabel">请确认如下操作</h3></div><div class="modal-body"></div><div class="modal-footer"><button class="btn" data-dismiss="modal" aria-hidden="true">取消</button><a class="btn btn-primary" id="dataConfirmOK">确定</a></div></div>');
//        }
//        $('#dataConfirmModal').find('.modal-body').text($(this).attr('data-confirm'));
//        $('#dataConfirmOK').attr('href', href);
//        $('#dataConfirmModal').modal({show:true});
//        return false;
//    });
});

function update_order_flag(order_id,status_flag,callback){
    var url = "/order/update_flag/"+order_id+"/"+status_flag;
    var req = $.ajax({
        url: url,
        dataType: 'json',
        type: 'POST'
    });

    req.done(function(data) {
        if (data.result == true) {
            callback();
        }
        else {
            bootbox.alert('操作失败：'+data.error);
        }
    });

    req.fail(function(request, status, error) {
        bootbox.alert('操作失败：'+data.error);
    });
}


function confirm(heading, question, cancelButtonTxt, okButtonTxt, callback) {
    var confirmModal =
        $('<div class="modal hide fade">' +
            '<div class="modal-header">' +
            '<a class="close" data-dismiss="modal" >&times;</a>' +
            '<h3>' + heading +'</h3>' +
            '</div>' +

            '<div class="modal-body">' +
            '<p>' + question + '</p>' +
            '</div>' +

            '<div class="modal-footer">' +
            '<a href="#" class="btn" data-dismiss="modal">' +
            cancelButtonTxt +
            '</a>' +
            '<a href="#" id="okButton" class="btn btn-primary">' +
            okButtonTxt +
            '</a>' +
            '</div>' +
            '</div>');

    confirmModal.find('#okButton').on('click',function(event) {
        callback();
        confirmModal.modal('hide');
    });
    confirmModal.modal('show');
};