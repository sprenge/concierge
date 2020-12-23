import { Component, Input, OnInit } from '@angular/core';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-unknown-person-list',
  templateUrl: './unknown-person-list.component.html',
  styleUrls: ['./unknown-person-list.component.scss']
})

@Injectable()
export class UnknownPersonListComponent implements OnInit {

  properties: any;
  shape_objects: any;
  public shape_id="all"
  public start_date="12/12/2020";
  public start_time="00:00";
  public end_date="12/12/2020";
  public end_time="00:00";
  url = "http://192.168.1.59:5107/interworking/api/v1.0/get_video_shapes/1608630978/1608630980"
  url2 = "http://192.168.1.59:5107/interworking/api/v1.0/get_shape_objects"

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.http.get(this.url).subscribe(
      data=>{
        this.properties=data;
      }
    );
    this.http.get(this.url2).subscribe(
      data=>{
        this.shape_objects=data;
      }
    );
  }

  clickFunction() {
    this.get_data();
    console.log(this.shape_id)

  }

  get_data() {
    this.http.get('http://192.168.1.59:5107/interworking/api/v1.0/get_video_shapes/1608630978/1608730980').subscribe(
      data=>{
        this.properties=data;
      }
    );
  }

}
