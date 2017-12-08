import groovy.lang.Binding;
import groovy.util.GroovyScriptEngine;
import groovy.util.ResourceException ;
import groovy.util.ScriptException ;
import java.io.IOException ;

public class EmGroovy {
  public static void main( String[] args ) throws IOException, ResourceException, ScriptException {
    String[] roots = new String[] { "." };
    GroovyScriptEngine gse = new GroovyScriptEngine(roots);
    Binding binding = new Binding();
    binding.setVariable("input", "world");
    System.out.println("hello!");
    gse.run("g1.groovy", binding);
    System.out.println(binding.getVariable("aResult")); // only work in class static ?
  }
}
//compile: javac -cp /usr/share/groovy2/embeddable/*:. EmGroovy.java
//run: java -cp /usr/share/groovy2/embeddable/*:. EmGroovy

/*test.groovy
class Est {  
  static SRESULT
  public static void main(String[] args) {
    println 'From Java: '+SRESULT
    SRESULT = 'bar'
  }
}*/

/*
import groovy.lang.Binding ;
import groovy.lang.GroovyShell ;
import java.io.File ;

public class Test {
    public static void main( String[] args ) throws Exception {
        Binding binding = new Binding() ;
        binding.setVariable( "SRESULT", "foo" ) ;

        GroovyShell gs = new GroovyShell( binding ) ;
        gs.evaluate( new File( "script.groovy" ) ) ;

        String sResult = (String)binding.getVariable( "SRESULT" ) ;
        System.out.printf( "FROM GROOVY: %s\n", sResult ) ;
    }
}*/
