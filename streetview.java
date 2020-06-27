import java.io.*;
import java.util.*;
import java.net.*;
import java.nio.file.*;

public class streetview {
	
	public static void main(String[] args) throws IOException {
		BufferedReader f = new BufferedReader(new FileReader("Centerline.csv"));
		/*
		ArrayList<Street> streets = parseData(f);
		
		findHeading(streets);
		System.out.println("Time: " + System.currentTimeMillis());
		System.out.println(streets.get(83).name);
		for(double[] arr : streets.get(83).points) {
			System.out.println(arr[0] + " " + arr[1]);
		}
		System.out.println(streets.get(83).avDist);
		System.out.println(streets.get(83).fov);
		System.out.println(streets.get(83).width);
		*/
		
		TreeCalc t = new TreeCalc(40.76050360780349, -73.96022079083882, 40.76052727, -73.96014289, 28.0);
		System.out.println(t.xy[0] + " " + t.xy[1]);
		System.out.println(t.imageY);
		
//		callAPI(streets.get(83));
		
		f.close();
	}
	
	static void callAPI(Street s) throws IOException {
		int count = 0;
		for(int i = 0; i < s.points.size(); i++) {
			double[] curr = s.points.get(i);
			String url = "https://maps.googleapis.com/maps/api/streetview?size=640x640&location=" + curr[0] + "," + curr[1] + 
						 "&fov=" + s.fov + "&heading=" + curr[2] + "&pitch=0&key=AIzaSyCKwmE_1aUZLozFXho7Vp9B9rQY4xUkRqU";
			try(InputStream in = new URL(url).openStream()){
			    Files.copy(in, Paths.get("C:/Allan/Streetview/img" + count + ".jpg"));
			}
			url = "https://maps.googleapis.com/maps/api/streetview?size=640x640&location=" + curr[0] + "," + curr[1] + 
				  "&fov=" + s.fov + "&heading=" + (curr[2] + 180) + "&pitch=0&key=AIzaSyCKwmE_1aUZLozFXho7Vp9B9rQY4xUkRqU";
			
			try(InputStream in = new URL(url).openStream()){
				Files.copy(in, Paths.get("C:/Allan/Streetview/img" + (count + 1)+ ".jpg"));
			}
			count += 2;
		}
	}
	
	static void findHeading(ArrayList<Street> streets) {
		for(Street s : streets) {
			for(int i = 1; i < s.points.size(); i++) {
				double[] left = s.points.get(i - 1);
				double[] right = s.points.get(i);
				Deg2UTM leftutm = new Deg2UTM(left[0], left[1]);
				Deg2UTM rightutm = new Deg2UTM(right[0], right[1]);
				double slope = -1 *  (rightutm.Northing - leftutm.Northing) / (rightutm.Easting - leftutm.Easting);
				slope = 1 / slope;
				double degrees = 90 - Math.toDegrees(Math.atan(slope));
				s.points.get(i - 1)[2] = Math.round(degrees);
				s.points.get(i)[2] = Math.round(degrees);
			}
		}
	}
	
	static ArrayList<Street> parseData(BufferedReader f) throws IOException {
		ArrayList<Street> streets = new ArrayList<>();
		f.readLine();
		System.out.println("Time: " + System.currentTimeMillis());
		while(f.ready()) {
			ArrayList<String> curr = split(f.readLine());
			int type = Integer.parseInt(curr.get(18));
			if(type != 1 || Integer.parseInt(curr.get(14)) == 0) continue;
			Street toAdd = new Street(findPoints(curr.get(3)), curr.get(10), Integer.parseInt(curr.get(14)) / 3.281);
			toAdd.avDist = findAvDist(toAdd.points);
			toAdd.fov = calculateFOV(toAdd);
			while(toAdd.fov > 100) {
				doublePoints(toAdd.points);
				toAdd.avDist = findAvDist(toAdd.points);
				toAdd.fov = calculateFOV(toAdd);
			}
			streets.add(toAdd);
		}
		System.out.println("Time: " + System.currentTimeMillis());
		return streets;
	}
	
	static void doublePoints(ArrayList<double[]> points) {
		for(int i = 1; i < points.size(); i++) {
			points.add(i, mid(points.get(i - 1)[0], points.get(i - 1)[1], points.get(i)[0], points.get(i)[1]));
			i++;
		}
	}
	
	static int calculateFOV(Street s) {
		return 2 * (int) Math.toDegrees(Math.atan(s.avDist / (s.width)));
	}
	
	static double findAvDist(ArrayList<double[]> points) {
		double sum = 0;
		for(int i = 1; i < points.size(); i++) {
			sum += FlatEarthDist.distance(points.get(i - 1)[0], points.get(i - 1)[1], points.get(i)[0], points.get(i)[1]);
		}
		return sum / (points.size() - 1);
	}
	
	static ArrayList<double[]> findPoints(String s) {
		s = s.substring(19, s.length() - 3);
		String[] sll = s.split(", ");
		ArrayList<double[]> result = new ArrayList<>();
		
		for(int i = 0; i < sll.length; i++) {
			String[] arr = sll[i].split(" ");
			result.add(new double[] {Double.parseDouble(arr[1]), Double.parseDouble(arr[0]), -1});
		}

		return result;
	}

	static double[] mid(double lat1, double lon1, double lat2, double lon2){

	    double dLon = Math.toRadians(lon2 - lon1);

	    //convert to radians
	    lat1 = Math.toRadians(lat1);
	    lat2 = Math.toRadians(lat2);
	    lon1 = Math.toRadians(lon1);

	    double Bx = Math.cos(lat2) * Math.cos(dLon);
	    double By = Math.cos(lat2) * Math.sin(dLon);
	    double lat3 = Math.atan2(Math.sin(lat1) + Math.sin(lat2), Math.sqrt((Math.cos(lat1) + Bx) * (Math.cos(lat1) + Bx) + By * By));
	    double lon3 = lon1 + Math.atan2(By, Math.cos(lat1) + Bx);

	    return new double[] {Math.toDegrees(lat3), Math.toDegrees(lon3), -1};
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
}
