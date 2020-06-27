import java.util.ArrayList;

public class Street {
	ArrayList<double[]> points; //lat, long, heading
	String name;
	double width; //in meters
	int fov = 90;
	double avDist = 0; //in meters
	
	public Street(ArrayList<double[]> p, String n, double w) {
		points = p;
		name = n;
		width = w;
	}
}