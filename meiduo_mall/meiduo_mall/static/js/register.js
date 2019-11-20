let vm = new Vue({
    el:'.app',
    delimiters: ['[[',']]'],
    data: {
        username: '',
        password: '',
        password2: '',
        mobile: '',
        allow: '',
        image_code_url: '',
        uuid: '',
        image_code: '',

        error_username: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,
        error_image_code: false,

        error_username_msg: '',
        error_mobile_msg: '',
        error_image_code_mag: '',
    },
    mounted(){ //监听页面是否加载完成
        this.generate_image_code();
    },
    methods:{
        generate_image_code(){
            this.uuid = generateUUID();
            this.image_code_url = '/image_codes/' + this.uuid + '/';
        },
        check_username(){
            let re=/^[a-zA-Z0-9_-]{5,20}$/;
            if (re.test(this.username)){
                this.error_username = false;
            }else {
                this.error_username_msg = '请输入5-20个字符的用户名';
                this.error_username = true;
            }

        //    发送ajax请求，判断用户名是否重复注册
            if (this.error_username==false){
                let url = '/usernames/'+this.username+'/count/';
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.count == 1){
                            // 用户名已存在
                            this.error_username_msg = '用户名已存在';
                            this.error_username = true;
                        }else{
                            this.error_username = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },
        check_password(){
            let re=/^[a-zA-Z0-9]{8,20}$/;
            if (re.test(this.password)){
                this.error_password = false;
            }else{
                this.error_password = true;
            }
        },
        check_password2(){
            if (this.password != this.password2){
                this.error_password2 = true;
            }else{
                this.error_password2 = false;
            }
        },
        check_mobile(){
            let re=/^1[3-9]\d{9}$/;
            if (re.test(this.mobile)){
                this.error_mobile = false;
            }else{
                this.error_mobile_msg = '您输入的手机号格式不正确';
                this.error_mobile = true;
            }
            if (this.error_mobile == false){
                let url = '/mobiles/'+this.mobile+'/count/';
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.count == 1){
                            this.error_mobile_msg = '手机号已存在';
                            this.error_mobile = true;
                        }else{this.error_mobile = false}
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },
        check_image_code(){
            if (this.image_code.length != 4){
                this.error_image_code_msg = '请填写图片验证码';
                this.error_image_code = true;
            }else{
                this.error_image_code = false;
            }
        },
        check_allow(){
            if (!this.allow){
                this.error_allow = true;
            }else{
                this.error_allow = false;
            }
        },
        on_submit(){
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_allow();

            if (this.error_username == true || this.error_password == true || this.error_password2 == true
                || this.error_mobile == true || this.error_allow == true) {
                // 禁用表单的提交
                window.event.returnValue = false;
            }
        }
    },
});