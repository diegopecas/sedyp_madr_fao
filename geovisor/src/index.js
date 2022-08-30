import './styles.css'
import './js/sidebar.js'
import {configs} from './config/config'
import {TermsAndConditions} from './js/TermsAndConditions'
import {IntroWalkThrough} from './js/IntroWalkThrough.js'

let termsAndConditionsModal = new TermsAndConditions(configs.texts.termsAndConditions)
termsAndConditionsModal.update({

    willClose: function(){ 
        if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)){
            $('.close').on('click', function(e) {
                document.getElementById("mymap").classList.remove('active');
                document.getElementById("right_sidebar").classList.remove('active');
            });
        }
        else{
            $('.close').on('click', function(e) {
                document.getElementById("mymap").classList.toggle('active');
                document.getElementById("right_sidebar").classList.toggle('active');
            });    

            document.getElementById("mymap").classList.toggle('active');
            document.getElementById("right_sidebar").classList.toggle('active');

            if( !JSON.parse( localStorage.getItem( 'walkthrough' ) ) ){
                new IntroWalkThrough()
            }
        }   
    }
})



