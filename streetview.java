import java.io.*;
import java.util.*;

public class streetview {
	
	public static void main(String[] args) throws IOException {
		BufferedReader f = new BufferedReader(new FileReader("Centerline.csv"));
		ArrayList<Street> streets = new ArrayList<>();
		f.readLine();
		
		while(f.ready()) {
			ArrayList<String> curr = split(f.readLine());
			int type = Integer.parseInt(curr.get(18));
			if(type == 4 || type == 11 || type == 12 || type == 14) continue;
			streets.add(new Street(findPoints(curr.get(3)), curr.get(10), Integer.parseInt(curr.get(14))));
		}
		
		for(Street s : streets) {
			System.out.println("Street: " + s.name + ", width: " + s.width);
			System.out.print("Points: ");
			for(double[] d : s.points) {
				System.out.print(d[0] + " " + d[1] + ", ");
			}
			System.out.println();
		}
		
		f.close();
	}
	
	static ArrayList<double[]> findPoints(String s) {
		s = s.substring(19, s.length() - 3);
		String[] sll = s.split(", ");
		double[][] longlat = new double[sll.length][2];
		
		for(int i = 0; i < sll.length; i++) {
			String[] arr = sll[i].split(" ");
			longlat[i] = new double[] {Double.parseDouble(arr[1]), Double.parseDouble(arr[0])};
		}
		
		ArrayList<double[]> result = new ArrayList<>();
		
		for(int i = 1; i < longlat.length; i++) {
			result.add(longlat[i - 1]);
			result.add(mid(longlat[i - 1][0], longlat[i - 1][1], longlat[i][0], longlat[i][1]));
		}
		result.add(longlat[sll.length - 1]);
		
		return result;
	}

	static double[] mid(double lon1, double lat1, double lon2, double lat2){

	    double dLon = Math.toRadians(lon2 - lon1);

	    //convert to radians
	    lat1 = Math.toRadians(lat1);
	    lat2 = Math.toRadians(lat2);
	    lon1 = Math.toRadians(lon1);

	    double Bx = Math.cos(lat2) * Math.cos(dLon);
	    double By = Math.cos(lat2) * Math.sin(dLon);
	    double lat3 = Math.atan2(Math.sin(lat1) + Math.sin(lat2), Math.sqrt((Math.cos(lat1) + Bx) * (Math.cos(lat1) + Bx) + By * By));
	    double lon3 = lon1 + Math.atan2(By, Math.cos(lat1) + Bx);

	    return new double[] {Math.toDegrees(lon3), Math.toDegrees(lat3)};
	}
	
	static ArrayList<String> split(String s) {
		ArrayList<String> result = new ArrayList<>();
		char[] arr = s.toCharArray();
		int prev = 0;
		boolean isGeom = false;
		for(int i = 0; i < arr.length; i++) {
			if(arr[i] == '(') isGeom = true;
			if(arr[i] == ')') isGeom = false;
			if(isGeom) continue;
			if(arr[i] == ',') {
				result.add(s.substring(prev, i));
				prev = i + 1;
			}
		}
		result.add(s.substring(prev));
		return result;
	}
	
	static class Street {
		ArrayList<double[]> points;
		String name;
		int width;
		
		public Street(ArrayList<double[]> p, String n, int w) {
			points = p;
			name = n;
			width = w;
		}
	}
}
