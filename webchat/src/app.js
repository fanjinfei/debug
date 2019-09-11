import Vue from 'vue'
import App from './App.vue'

Vue.component('todo-item', {
  // The todo-item component now accepts a
  // "prop", which is like a custom attribute.
  // This prop is called todo.
  props: ['todo'],
  template: '<li>{{ todo.text }}</li>'
})

Vue.component('awesome-button', {
  template: `<button @click="clickHandler">Click me for some awesomeness</button>`,
  props: ['tlist', 'userq'],
  methods: {
    clickHandler() {
      this.tlist.push( { id:6, text: 'another again ' + this.userinput } );
      console.log(this.userinput);
      //alert('YAAAS 😎');
      
    }
  },
  computed: {
     userinput() {
       let data = this.userq;
       return data;
     }
  }
});

var app=new Vue({
  el: "#app",
  components: { App },
  template: "<App/>"
});

// Define a new component called todo-item
/*
Vue.component('todo-item', {
  // The todo-item component now accepts a
  // "prop", which is like a custom attribute.
  // This prop is called todo.
  props: ['todo'],
  template: '<li>{{ todo.text }}</li>'
})

new Vue({
  el: '#app',
 data: {
    groceryList: [
      { id: 0, text: 'Vegetables' },
      { id: 1, text: 'Cheese' },
      { id: 2, text: 'Whatever else humans are supposed to eat' }
    ]
  },
  template: '<div> \
    <h1>Hello World!</h1> \
    <ol> \
        <todo-item \
          v-for="item in groceryList" \
          v-bind:todo="item" \
          v-bind:key="item.id" \
        ></todo-item> \
    </ol> \
  </div>' ,
  
//  render: h => h(App)
})
*/



