
        function add(submiturl) {
            $('#add-class').click(function () {
                $("#error-msg").empty();
                $('.add input').val('');
                 SUBMITURL = submiturl;
                $('.self-modal,.add').removeClass('hide')
            })
        }
        function closeModal() {
            $('#close-widow,.cancel').click(function () {
                $('.self-modal,.window').addClass('hide')
            })
        }
        function submit(Info) {
                  console.log(Info);
                  $.ajax({
                      url: SUBMITURL,
                      type:'POST',
                      data:Info,
                      dataType:'json',
                      success:function (data) {
                          if (data.status){
                              location.reload()
                          }else {
                            console.log(data.msg);
                            $("#error-msg").text(data.msg)
                          }
                      }
                  })


        }

        function deleteMethod(submiturl) {
            $('.td-delete').click(function () {
                $('.self-modal,.delete').removeClass('hide');
                var tds = $(this).parent().prevAll();
                var nid = tds.eq(3).html();
                $('.delete-modal .confirm').attr('href',submiturl+nid)
            })
        }

        function edit(submiturl) {
            $('.td-edit').click(function () {
                $("#error-msg").empty();
                $('.self-modal, .add').removeClass('hide');
                var tds = $(this).parent().prevAll();
                /*
                var nid = tds.eq(2).html();
                var course = tds.eq(0).html();
                var class_name = tds.eq(1).html();
                $(".add #class").val(class_name);
                $(".add #course ").val(course);
                $("#"+course).prop('selected', true);
                $('.add span[id="nid"]').html(nid);
                SUBMITURL = /edit_class/;
                */
                // 使用循环的写法
                $(this).parent().prevAll().each(function () {
                    var text = $(this).text();
                    var name = $(this).attr('harry');
                    console.log(name);
                    $('.add [name='+name+']').val(text);
                    if (name=='course'){
                         $("#"+text).prop('selected', true);
                    }
                });
                SUBMITURL = submiturl;
            });
        }
