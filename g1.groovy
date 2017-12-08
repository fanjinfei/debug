//learn groovy
//to run: groovy g1.groovy or from EmGroovy.java

System.out.println("Hello World");

//println input // from java binding

def x = 42, y= "hi", fname="asdf"
println x.getClass()
println y.getClass()
println "hi ${fname[1]} . $y"

def helloWorld = {
  println "Hello World"
}

def power = { int x1, int y1 -> //confilict with x
  return Math.pow(x1, y1)
}

println power(2, 3) // Will print 8.0
helloWorld()

def transform = { str, transformation ->
  transformation(str)
}

println transform("Hello World", { it.toUpperCase() })

def createGreeter = { name ->
  return {
    def day = new Date().getDay()
    if (day == 0 || day == 6) {
      println "Nice Weekend, $name"
    } else {
      println "Hello, $name"
    }
  }
}
def greetWorld = createGreeter("World")
greetWorld()


void m(Integer x) {        
  println "in m(Integer)"
}

m(1)

def key = 'Key3'
def aMap = [
  'Key1': 'Value 1', // Put key1 -> Value 1 to the map
  Key2: 'Value 2', // You can also skip the quotes, the key will automatically be a String
  (key): 'Another value' // If you want the key to be the value of a variable, you need to put it in parantheses
]
println aMap[key]


def baseDir="/tmp/"
new File(baseDir,'haiku.txt').withWriter('utf-8') { writer ->
    writer.writeLine 'Into the ancient pond'
    writer.writeLine 'A frog jumps'
    writer.writeLine 'Water’s sound!'
}

new File(baseDir, 'haiku.txt').eachLine { line ->
    println line
}

def list = [5, 6, 7, 8]
assert list.get(2) == 7
assert list[2] == 7
assert list instanceof java.util.List
list.add(5)
println list



class Person {                       

    String name                      
    Integer age

    def increaseAge(Integer years) { 
        this.age += years
    }
}

Person ap = new Person(name:"Bob", age:76)
println ap

//def process = "ls -l".execute()             
//println "Found text ${process.text}"  

aResult = "hello"

// MyGroovyTest.groovy
class MyGroovyTest {
  static Result
  def sayHello() {
    println 'Hello From MyGroovyTest'
  }
  static void main(args) {
    def mgt = new MyGroovyTest()
    mgt.sayHello()
    Result = "hi"
  }
}

MyGroovyTest.main()
