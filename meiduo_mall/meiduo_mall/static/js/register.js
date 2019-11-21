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
        sms_code: '',
        sms_code_tip: '获取短信验证码',

        error_username: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code: false,
        sending_flag: false,

        error_username_msg: '',
        error_mobile_msg: '',
        error_image_code_msg: '',
        error_sms_code_msg: '',
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
        send_sms_code(){
            if (this.sending_flag == true){
                return;
            }
            this.sending_flag = true;

            this.check_mobile();
            this.check_image_code();
            if (this.error_mobile == true || this.error_image_code == true){
                this.sending_flag = false;
                return;
            }

            //请求短信验证码
            let url = '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&uuid=' + this.uuid;
            axios.get(url, {
                responseType: 'json'
            })
                .then(response => {
                    if (response.data.code == '0'){
                        let num = 60;
                        let t=setInterval(()=>{
                            if (num == 1){
                                clearInterval(t);
                                this.sms_code_tip = '获取短信验证码';
                                this.generate_image_code();
                                this.sending_flag = false;
                            }else{
                                num -= 1;
                                this.sms_code_tip = num + '秒';
                            }
                        }, 1000)
                    }else{
                        if (response.data.code == '4001'){
                            this.error_image_code_msg = response.data.errmsg;
                            this.error_image_code = true;
                        }else{
                            this.error_sms_code_msg = response.data.errmsg;
                            this.error_sms_code = true;
                        }
                        this.generate_image_code();
                        this.sending_flag = false;
                    }
                })
                .catch(error => {
                    console.log(error.response);
                    this.sending_flag = false;
                })
        },
        check_sms_code(){
            if (this.sms_code.length != 6){
                this.error_sms_code_msg = '请填写短信验证码';
                this.error_sms_code = true;
            }else{
                this.error_sms_code = false;
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
            this.check_sms_code();
            this.check_allow();

            if (this.error_username == true || this.error_password == true || this.error_password2 == true
                || this.error_mobile == true || this.error_allow == true) {
                // 注册参数不全，禁用表单的提交
                window.event.returnValue = false;
            }
        }
    },
});